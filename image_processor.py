"""Image preprocessing utilities for better OCR results."""
import io
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image, ExifTags


def fix_image_orientation(img: Image.Image) -> Image.Image:
    """Fix image orientation based on EXIF data."""
    try:
        exif = img._getexif()
        if exif is None:
            return img

        orientation_key = None
        for key, val in ExifTags.TAGS.items():
            if val == 'Orientation':
                orientation_key = key
                break

        if orientation_key is None or orientation_key not in exif:
            return img

        orientation = exif[orientation_key]

        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)

        return img
    except Exception:
        return img


def load_image(image_path_or_bytes) -> Tuple[Image.Image, np.ndarray]:
    """Load image from path or bytes, fix orientation, return PIL and numpy array."""
    try:
        import cv2
    except ImportError:
        cv2 = None

    if isinstance(image_path_or_bytes, bytes):
        pil_img = Image.open(io.BytesIO(image_path_or_bytes))
    else:
        # Handle Japanese file paths
        if cv2:
            img_array = np.fromfile(str(image_path_or_bytes), dtype=np.uint8)
            cv_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            pil_img = Image.open(image_path_or_bytes)
        else:
            pil_img = Image.open(image_path_or_bytes)

    # Fix EXIF orientation
    pil_img = fix_image_orientation(pil_img)

    # Convert to numpy array (BGR for OpenCV)
    if pil_img.mode == 'RGBA':
        pil_img = pil_img.convert('RGB')

    img_array = np.array(pil_img)

    if cv2 and len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    return pil_img, img_array


def preprocess_image_variants(img_cv: np.ndarray) -> List[Tuple[str, np.ndarray]]:
    """Generate multiple preprocessing variants for better OCR results.

    Args:
        img_cv: Image in OpenCV BGR format

    Returns:
        List of (variant_name, processed_image) tuples
    """
    try:
        import cv2
    except ImportError:
        return [('original', img_cv)]

    variants = []

    # Original
    variants.append(('original', img_cv))

    # Grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    variants.append(('grayscale', cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))

    # Contrast enhancement (CLAHE)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    variants.append(('contrast_enhanced', enhanced))

    # Sharpening
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(img_cv, -1, kernel)
    variants.append(('sharpened', sharpened))

    # Binary (adaptive threshold)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
    variants.append(('binary', cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)))

    # Brightness adjustment
    bright = cv2.convertScaleAbs(img_cv, alpha=1.3, beta=30)
    variants.append(('brightened', bright))

    return variants


def try_rotations(img_cv: np.ndarray, reader) -> Tuple[List, int]:
    """Try OCR at different rotations to find best orientation.

    Args:
        img_cv: Image in OpenCV BGR format
        reader: EasyOCR reader instance

    Returns:
        Tuple of (best_results, best_angle)
    """
    try:
        import cv2
    except ImportError:
        return [], 0

    best_results = []
    best_angle = 0
    best_confidence = 0

    for angle in [0, 90, 180, 270]:
        if angle == 0:
            rotated = img_cv
        else:
            h, w = img_cv.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

            cos = abs(matrix[0, 0])
            sin = abs(matrix[0, 1])
            new_w = int(h * sin + w * cos)
            new_h = int(h * cos + w * sin)
            matrix[0, 2] += (new_w - w) / 2
            matrix[1, 2] += (new_h - h) / 2

            rotated = cv2.warpAffine(img_cv, matrix, (new_w, new_h),
                                      borderValue=(255, 255, 255))

        try:
            results = reader.readtext(rotated)
            if results:
                avg_conf = sum(r[2] for r in results) / len(results)
                score = len(results) * avg_conf
                if score > best_confidence:
                    best_confidence = score
                    best_results = results
                    best_angle = angle
        except Exception:
            continue

    return best_results, best_angle


def image_to_bytes(image: Image.Image, format: str = 'JPEG') -> bytes:
    """Convert PIL Image to bytes."""
    buffer = io.BytesIO()
    if image.mode == 'RGBA' and format.upper() == 'JPEG':
        image = image.convert('RGB')
    image.save(buffer, format=format)
    return buffer.getvalue()
