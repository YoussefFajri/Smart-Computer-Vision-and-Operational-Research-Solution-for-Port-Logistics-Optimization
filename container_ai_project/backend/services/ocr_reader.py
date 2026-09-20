"""
OCR Reader — Robust Multi-Orientation Pipeline
────────────────────────────────────────────────
Receives bounding box crops from YOLO and returns container IDs.
Handles horizontal, vertical, and rotated text reliably.

Container ID format (ISO 6346):
  [A-Z]{4}[0-9]{6}[0-9]   e.g.  MSCU1234567  CMAU9876543

Key improvements over previous version:
  - OpenCV-based skew/orientation detection (no Tesseract required)
  - Optional pytesseract OSD for precise rotation angle
  - EasyOCR rotation_info=[90, 180, 270] for internal multi-angle search
  - Character allowlist (A-Z, 0-9 only)
  - Improved preprocessing: resize, grayscale, Gaussian blur, adaptive threshold
  - Standalone process_image(image_bytes) for Kafka integration
"""
from __future__ import annotations
import re
import time
import base64
import logging
from typing import Optional

import cv2
import numpy as np

# ── Logging ────────────────────────────────────────────────────────────────────
logger = logging.getLogger("ocr_reader")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[OCR] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ── Container ID regex (ISO 6346) ──────────────────────────────────────────────
CONTAINER_ID_PATTERN = re.compile(r"\b[A-Z]{4}\s*\d{6,7}\b")

# ── Character allowlist for EasyOCR ────────────────────────────────────────────
ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# ── Confidence threshold ──────────────────────────────────────────────────────
MIN_CONFIDENCE = 0.4

# ── Max image dimension for preprocessing ─────────────────────────────────────
MAX_DIM = 800

# ── Optional pytesseract import ────────────────────────────────────────────────
_TESSERACT_AVAILABLE = False
try:
    import pytesseract
    # Quick check that Tesseract binary is accessible
    pytesseract.get_tesseract_version()
    _TESSERACT_AVAILABLE = True
    logger.info("pytesseract disponible — OSD activé.")
except Exception:
    logger.info("pytesseract non disponible — utilisation d'OpenCV pour la détection d'orientation.")


# ═══════════════════════════════════════════════════════════════════════════════
#  Standalone function: process raw image bytes → OCR results
# ═══════════════════════════════════════════════════════════════════════════════

def process_image(image_bytes: bytes) -> dict:
    """
    Process raw image bytes (JPEG/PNG) through the full OCR pipeline.

    This is the main entry point for Kafka integration.
    It decodes the image, detects orientation, preprocesses, runs EasyOCR,
    and returns the best container ID found.

    Args:
        image_bytes: Raw JPEG or PNG bytes (or base64-encoded string).

    Returns:
        dict with keys:
          - raw_text:       All detected text joined
          - container_id:   Extracted ISO 6346 ID or None
          - ocr_confidence: Average confidence score
          - is_valid:       True if a valid container ID was found
          - pipeline:       Name of the pipeline that produced the result
          - ocr_time:       Processing time in seconds
    """
    t0 = time.perf_counter()

    # Handle base64-encoded input
    if isinstance(image_bytes, str):
        try:
            image_bytes = base64.b64decode(image_bytes)
        except Exception as e:
            logger.error(f"Échec du décodage base64: {e}")
            return _empty_result()

    # Decode to OpenCV image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        logger.error("Impossible de décoder l'image.")
        return _empty_result()

    # Run the full OCR pipeline
    reader = OCRReader()
    result = reader.read_from_crop(image)
    result["ocr_time"] = round(time.perf_counter() - t0, 3)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  Helper: empty result
# ═══════════════════════════════════════════════════════════════════════════════

def _empty_result() -> dict:
    return {
        "raw_text":       "",
        "container_id":   None,
        "ocr_confidence": 0.0,
        "is_valid":       False,
        "ocr_time":       0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  OCRReader Class
# ═══════════════════════════════════════════════════════════════════════════════

class OCRReader:
    """
    Wraps EasyOCR for container ID extraction with robust multi-orientation support.

    Usage:
        reader = OCRReader()
        result = reader.read_from_crop(crop_image)
    """

    def __init__(self, languages: list[str] = None):
        self.languages = languages or ["en"]
        self.reader = None   # lazy-load on first use
        logger.info("OCR Reader initialisé (EasyOCR chargé à la première détection).")

    def _get_reader(self):
        """Lazy-load EasyOCR on first call to spread RAM cost."""
        if self.reader is None:
            try:
                import easyocr
                import torch
                # Detect GPU status
                gpu_available = torch.cuda.is_available()
                # Limit PyTorch CPU threads to 1 to avoid high multi-threading overhead
                logger.info(f"Configuration des threads PyTorch CPU à 1... (GPU disponible: {gpu_available})")
                torch.set_num_threads(1)

                logger.info(f"Chargement EasyOCR... (première fois, ~10s, GPU={gpu_available})")
                self.reader = easyocr.Reader(
                    self.languages,
                    gpu=gpu_available,
                    verbose=False,
                    download_enabled=False,
                )
                logger.info("EasyOCR prêt !")
            except Exception as e:
                logger.warning(f"Impossible de charger EasyOCR: {e}")
                self.reader = "FAILED"
        return self.reader if self.reader != "FAILED" else None

    # ══════════════════════════════════════════════════════════════════════════
    #  Image Preprocessing Pipelines
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _resize_max(img: np.ndarray, max_dim: int = MAX_DIM) -> np.ndarray:
        """Resize image so that the longest side is at most max_dim pixels."""
        h, w = img.shape[:2]
        if max(h, w) <= max_dim:
            return img
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    @staticmethod
    def _upscale_small(img: np.ndarray, min_dim: int = 500) -> np.ndarray:
        """Upscale small images so OCR can read them better."""
        h, w = img.shape[:2]
        if max(h, w) < min_dim:
            scale = min_dim / max(h, w)
            return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Also upscale if the SHORT side is very narrow (e.g. vertical text crop 105px wide)
        if min(h, w) < 200:
            scale = 200 / min(h, w)
            return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        return img

    @staticmethod
    def _preprocess_standard(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 1 — Standard: resize + CLAHE contrast enhancement.
        Best for well-lit images with moderate contrast.
        """
        # Upscale small crops
        img = OCRReader._upscale_small(img)
        # CLAHE on LAB luminance channel
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    @staticmethod
    def _preprocess_binary(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 2 — Binary: grayscale + Gaussian blur + adaptive threshold.
        Best for noisy/low-contrast images. Produces a clean black/white image.
        """
        img = OCRReader._upscale_small(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # CLAHE on grayscale for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        blurred = clahe.apply(blurred)
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11, C=2
        )
        # Convert back to BGR for EasyOCR
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _preprocess_sharpen(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 3 — Sharpen: denoise + sharpen kernel.
        Best for blurry camera images.
        """
        img = OCRReader._upscale_small(img)
        h, w = img.shape[:2]
        if max(h, w) < 500:
            # Denoise small images (slow on large ones)
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            denoised = img
        # Sharpen kernel
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(denoised, -1, kernel)

    @staticmethod
    def _preprocess_inverted(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 4 — Inverted binary: for light text on dark background.
        """
        img = OCRReader._upscale_small(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Otsu threshold + invert
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _preprocess_otsu(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 5 — Otsu: CLAHE + Otsu global threshold.
        Best for real camera footage with uneven lighting and motion blur.
        More aggressive binarization than adaptive threshold.
        """
        img = OCRReader._upscale_small(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # CLAHE to normalize lighting
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # Bilateral filter to preserve edges while reducing noise
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
        # Otsu threshold
        _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _preprocess_color_isolate(img: np.ndarray) -> np.ndarray:
        """
        Pipeline 6 — Color Isolate: Extract white/bright text from colored backgrounds.
        Critical for red, blue, green containers where standard grayscale OCR fails
        because the text has low luminance contrast against the colored background.

        Strategy:
          1. Convert to HSV
          2. Create mask for bright, low-saturation pixels (= white/light text)
          3. Also try grayscale channel that maximizes contrast
          4. Combine and threshold
        """
        img = OCRReader._upscale_small(img)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h_ch, s_ch, v_ch = cv2.split(hsv)

        # Method 1: HSV-based white text isolation
        # White text has low saturation and high value
        white_mask = cv2.inRange(hsv, (0, 0, 140), (180, 80, 255))

        # Method 2: Use the channel with max contrast
        # For red containers, the red channel is high everywhere -> use blue or green
        b, g, r = cv2.split(img)
        # Pick the channel with the highest std (most contrast)
        stds = [np.std(b), np.std(g), np.std(r)]
        best_ch = [b, g, r][np.argmax(stds)]

        # CLAHE on the best channel
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(best_ch)

        # Otsu threshold on the best channel
        _, ch_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Combine both methods: union of white mask and channel threshold
        combined = cv2.bitwise_or(white_mask, ch_thresh)

        # Clean up with morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)

        return cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)

    # ══════════════════════════════════════════════════════════════════════════
    #  Orientation Detection
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _detect_skew_opencv(img: np.ndarray) -> float:
        """
        Detect the skew angle of text in the image using OpenCV contour analysis.
        Returns the angle in degrees that the image should be rotated to straighten text.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        # Dilate to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return 0.0

        # Filter out tiny contours
        min_area = img.shape[0] * img.shape[1] * 0.001
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        if not valid_contours:
            return 0.0

        # Get angles from minAreaRect of the largest contours
        angles = []
        for c in sorted(valid_contours, key=cv2.contourArea, reverse=True)[:10]:
            rect = cv2.minAreaRect(c)
            angle = rect[2]
            w, h = rect[1]
            # Normalize angle: minAreaRect returns angles in [-90, 0)
            if w < h:
                angle = angle - 90
            angles.append(angle)

        if not angles:
            return 0.0

        # Use median angle for robustness
        median_angle = float(np.median(angles))

        # Only correct small skews (< 45°) — large rotations are handled separately
        if abs(median_angle) > 45:
            return 0.0

        return median_angle

    @staticmethod
    def _detect_orientation_tesseract(img: np.ndarray) -> Optional[int]:
        """
        Use pytesseract OSD to detect the dominant rotation angle.
        Returns the rotation angle (0, 90, 180, 270) or None if unavailable.
        """
        if not _TESSERACT_AVAILABLE:
            return None
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # pytesseract needs a PIL Image or numpy array
            osd = pytesseract.image_to_osd(gray, output_type=pytesseract.Output.DICT)
            rotate = osd.get("rotate", 0)
            confidence = osd.get("orientation_conf", 0)
            logger.info(f"Tesseract OSD: rotation={rotate}°, confidence={confidence:.1f}")
            if confidence > 1.0:  # OSD confidence is quite low-scale
                return int(rotate)
        except Exception as e:
            logger.warning(f"Tesseract OSD failed: {e}")
        return None

    @staticmethod
    def _deskew_image(img: np.ndarray, angle: float) -> np.ndarray:
        """Rotate the image by the given angle to correct skew."""
        if abs(angle) < 0.5:
            return img
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Compute new bounding box to avoid clipping
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)
        M[0, 2] += (new_w - w) / 2
        M[1, 2] += (new_h - h) / 2
        return cv2.warpAffine(img, M, (new_w, new_h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    @staticmethod
    def _rotate_90(img: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by 90, 180, or 270 degrees."""
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    @staticmethod
    def _rotate_if_vertical(img: np.ndarray, force_vertical: bool = False) -> tuple[np.ndarray, bool]:
        """
        If the image crop is taller than wide (vertical text), rotate it 90° clockwise
        so that the text becomes horizontal for OCR.
        """
        h, w = img.shape[:2]
        if force_vertical or h > w * 1.3:
            rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            return rotated, True
        return img, False

    # ══════════════════════════════════════════════════════════════════════════
    #  Vertical Text: Segment & Stitch Characters
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _segment_and_stitch_vertical(img: np.ndarray) -> Optional[np.ndarray]:
        """
        Segment a vertically aligned text crop into individual stacked characters
        using contour/connected component analysis, and stitch them horizontally.
        """
        h, w = img.shape[:2]
        if h <= w * 1.1:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Estimate background color from borders
        border_mean = (np.mean(gray[:5, :]) + np.mean(gray[-5:, :]) +
                       np.mean(gray[:, :5]) + np.mean(gray[:, -5:])) / 4.0

        if border_mean > 127:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Close gaps in characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)

        components = []
        for label in range(1, num_labels):
            x_c, y_c, w_c, h_c, area = stats[label]

            if area < 25 or w_c < 3 or h_c < 7:
                continue
            if w_c > w * 0.9 and h_c < 10:
                continue

            cx, cy = centroids[label]
            dist_from_center = abs(cx - w / 2)
            if dist_from_center > w * 0.45:
                continue

            components.append({
                "bbox": (x_c, y_c, w_c, h_c),
                "y": y_c,
                "h": h_c,
                "w": w_c
            })

        if not components:
            return None

        # Sort top-to-bottom
        components = sorted(components, key=lambda c: c["y"])

        # Merge vertically close components
        merged_components = []
        for comp in components:
            if not merged_components:
                merged_components.append(comp)
                continue

            last = merged_components[-1]
            last_x, last_y, last_w, last_h = last["bbox"]
            x_c, y_c, w_c, h_c = comp["bbox"]

            if y_c <= last_y + last_h + 8:
                new_y = min(last_y, y_c)
                new_h = max(last_y + last_h, y_c + h_c) - new_y
                new_x = min(last_x, x_c)
                new_w = max(last_x + last_w, x_c + w_c) - new_x
                merged_components[-1] = {
                    "bbox": (new_x, new_y, new_w, new_h),
                    "y": new_y,
                    "h": new_h,
                    "w": new_w
                }
            else:
                merged_components.append(comp)

        valid_crops = []
        for comp in merged_components:
            x_c, y_c, w_c, h_c = comp["bbox"]
            if h_c < 8 or w_c < 4:
                continue

            pad = 2
            x1 = max(0, x_c - pad)
            y1 = max(0, y_c - pad)
            x2 = min(w, x_c + w_c + pad)
            y2 = min(h, y_c + h_c + pad)

            char_crop = img[y1:y2, x1:x2]
            if char_crop.size > 0:
                valid_crops.append(char_crop)

        if len(valid_crops) < 2:
            return None

        # Resize to fixed height, keeping aspect ratio
        target_h = 120
        resized_crops = []
        for c in valid_crops:
            ch, cw = c.shape[:2]
            aspect = cw / ch
            target_w = max(10, int(target_h * aspect))
            rc = cv2.resize(c, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
            resized_crops.append(rc)

        # Stitch horizontally with a white gap
        gap_w = 15
        gap = np.ones((target_h, gap_w, 3), dtype=np.uint8) * 255
        stitched = np.ones((target_h, 15, 3), dtype=np.uint8) * 255
        for i, rc in enumerate(resized_crops):
            stitched = np.hstack([stitched, rc])
            if i < len(resized_crops) - 1:
                stitched = np.hstack([stitched, gap])

        stitched = np.hstack([stitched, np.ones((target_h, 15, 3), dtype=np.uint8) * 255])
        return stitched

    # ══════════════════════════════════════════════════════════════════════════
    #  Core OCR: Run EasyOCR with rotation_info and allowlist
    # ══════════════════════════════════════════════════════════════════════════

    def _run_easyocr(self, img: np.ndarray, use_rotation: bool = True) -> list:
        """
        Run EasyOCR on the image with optional rotation_info and character allowlist.
        Returns list of (bbox, text, confidence) tuples.
        """
        reader = self._get_reader()
        if reader is None:
            return []

        kwargs = {
            "paragraph": False,
            "allowlist": ALLOWLIST,
        }
        # rotation_info lets EasyOCR internally try 0°, 90°, 180°, 270°
        if use_rotation:
            kwargs["rotation_info"] = [90, 180, 270]

        try:
            results = reader.readtext(img, **kwargs)
            return results
        except Exception as e:
            logger.warning(f"EasyOCR readtext failed: {e}")
            return []

    def _ocr_to_result(self, results: list, pipeline_name: str) -> dict:
        """Convert EasyOCR results list to a standardized result dict."""
        if not results:
            return {
                "raw_text":       "",
                "container_id":   None,
                "ocr_confidence": 0.0,
                "is_valid":       False,
                "pipeline":       pipeline_name,
            }

        # Filter by confidence
        filtered = [(bbox, text, conf) for bbox, text, conf in results if conf >= MIN_CONFIDENCE]

        if not filtered:
            # Fall back to all results if nothing passes the threshold
            filtered = results

        raw_text = " ".join([r[1] for r in filtered]).upper().strip()
        confidence = float(np.mean([r[2] for r in filtered]))
        container_id = self._extract_container_id(raw_text)

        return {
            "raw_text":       raw_text,
            "container_id":   container_id,
            "ocr_confidence": round(confidence, 4),
            "is_valid":       container_id is not None,
            "pipeline":       pipeline_name,
        }

    # ══════════════════════════════════════════════════════════════════════════
    #  Main OCR Entry Point: read_from_crop
    # ══════════════════════════════════════════════════════════════════════════

    def read_from_crop(self, crop: np.ndarray, yolo_class: str = "") -> dict:
        """
        Run OCR on a single crop. Tries multiple preprocessing pipelines
        and candidate orientations, prioritising the most likely ones and exiting early.

        Strategy:
          1. Detect orientation (OpenCV skew + optional Tesseract OSD)
          2. Correct skew/rotation
          3. Try multiple preprocessing pipelines with rotation_info
          4. For vertical text: try segment-and-stitch approach
          5. Early exit as soon as a valid ISO 6346 container ID is found
        """
        import gc
        t0 = time.perf_counter()

        if crop is None or crop.size == 0:
            return _empty_result()

        reader = self._get_reader()
        if reader is None:
            return {
                "raw_text":       "OCR_UNAVAILABLE",
                "container_id":   "INCONNU",
                "ocr_confidence": 0.0,
                "is_valid":       False,
                "ocr_time":       0.0,
            }

        h, w = crop.shape[:2]
        force_vertical = "vertical" in yolo_class.lower()
        force_horizontal = "horizontal" in yolo_class.lower()
        is_vertical = force_vertical or (h > w * 1.3 and not force_horizontal)

        logger.info(f"Crop: {w}x{h}, class='{yolo_class}', "
                    f"vertical={'oui' if is_vertical else 'non'}")

        # ── Step 1: Orientation detection & correction ─────────────────────────

        # 1a. Try Tesseract OSD for precise rotation detection
        corrected = crop.copy()
        tesseract_angle = self._detect_orientation_tesseract(crop)
        if tesseract_angle and tesseract_angle != 0:
            corrected = self._rotate_90(crop, tesseract_angle)
            logger.info(f"Tesseract OSD correction: rotation de {tesseract_angle}°")

        # 1b. OpenCV skew detection for fine-tuning
        skew_angle = self._detect_skew_opencv(corrected)
        if abs(skew_angle) > 1.0:
            corrected = self._deskew_image(corrected, skew_angle)
            logger.info(f"OpenCV deskew: correction de {skew_angle:.1f}°")

        # ── Step 2: Build candidate images ─────────────────────────────────────

        candidates = []

        if is_vertical:
            # Try stitched (highly probable for vertical container IDs)
            try:
                stitched = self._segment_and_stitch_vertical(crop)
                if stitched is not None:
                    candidates.append(("stitched", stitched))
                    logger.info("Caractères verticaux assemblés horizontalement.")
            except Exception as e:
                logger.warning(f"Assemblage vertical échoué: {e}")

            # Try 90° CW rotation
            rotated_cw = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
            candidates.append(("90cw", rotated_cw))

            # Try 90° CCW rotation
            rotated_ccw = cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
            candidates.append(("90ccw", rotated_ccw))

            # Try the corrected image (skew-corrected)
            candidates.append(("corrected", corrected))

            # Try original
            candidates.append(("original", crop))
        else:
            # Horizontal text — corrected image first
            candidates.append(("corrected", corrected))

            # Try original
            if tesseract_angle or abs(skew_angle) > 1.0:
                candidates.append(("original", crop))

            # Try 180° (upside down)
            candidates.append(("180", cv2.rotate(crop, cv2.ROTATE_180)))

            # Also try 90° rotations for horizontal crops — sometimes the crop
            # is actually vertical but YOLO/aspect-ratio detection got it wrong
            rotated_cw = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
            candidates.append(("90cw", rotated_cw))

            rotated_ccw = cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
            candidates.append(("90ccw", rotated_ccw))

        # ── Step 3: Preprocessing pipelines ────────────────────────────────────

        pipelines = [
            ("standard",  self._preprocess_standard),
            ("binary",    self._preprocess_binary),
            ("sharpen",   self._preprocess_sharpen),
            ("inverted",  self._preprocess_inverted),
            ("otsu",      self._preprocess_otsu),
            ("color",     self._preprocess_color_isolate),
        ]

        # ── Step 4: Search candidates × pipelines ─────────────────────────────

        best_result = None
        best_score = -1.0

        for orient_name, orient_img in candidates:
            for pipe_name, pipe_fn in pipelines:
                try:
                    processed = pipe_fn(orient_img)
                    # Use rotation_info to let EasyOCR also try internal rotations
                    results = self._run_easyocr(processed, use_rotation=True)

                    result = self._ocr_to_result(results, f"{orient_name}_{pipe_name}")
                    container_id = result.get("container_id")
                    confidence = result.get("ocr_confidence", 0.0)

                    # Score: valid ID gets a huge bonus
                    score = confidence + (10.0 if container_id else 0.0)

                    if score > best_score:
                        best_score = score
                        best_result = result

                    # Early exit — valid ID found with decent confidence
                    if container_id and confidence > 0.25:
                        best_result["ocr_time"] = round(time.perf_counter() - t0, 3)
                        logger.info(f"[OK] Container ID trouvé: {container_id} "
                                    f"(pipeline={pipe_name}, orient={orient_name}, "
                                    f"conf={confidence:.2f})")
                        gc.collect()
                        return best_result

                except Exception as e:
                    logger.warning(f"Pipeline {orient_name}/{pipe_name} échoué: {e}")
                finally:
                    gc.collect()

        # ── Step 5: Final result ───────────────────────────────────────────────

        if best_result is None:
            best_result = _empty_result()

        best_result["ocr_time"] = round(time.perf_counter() - t0, 3)

        if best_result.get("container_id"):
            logger.info(f"[OK] Container ID trouvé: {best_result['container_id']} "
                        f"(pipeline={best_result.get('pipeline')}, "
                        f"conf={best_result['ocr_confidence']:.2f})")
        else:
            logger.warning(f"Aucun ID trouvé. Texte brut: "
                          f"'{best_result.get('raw_text', '')[:80]}'")

        return best_result

    # ── Lightweight single-pass OCR ────────────────────────────────────────────

    def read_from_crop_light(self, crop: np.ndarray) -> dict:
        """
        Lightweight single-pass version of OCR.
        Uses rotation_info and allowlist but only one preprocessing pipeline.
        Perfect for full-frame camera fallbacks.
        """
        t0 = time.perf_counter()
        if crop is None or crop.size == 0:
            return _empty_result()

        reader = self._get_reader()
        if reader is None:
            return _empty_result()

        try:
            # Resize large images to prevent OOM
            resized = self._resize_max(crop, MAX_DIM)
            # Run EasyOCR with rotation_info and allowlist
            results = self._run_easyocr(resized, use_rotation=True)

            result = self._ocr_to_result(results, "light_rotation")
            result["ocr_time"] = round(time.perf_counter() - t0, 3)

            if result.get("container_id"):
                logger.info(f"[OK] Light OCR trouvé: {result['container_id']} "
                           f"(conf={result['ocr_confidence']:.2f})")
            return result
        except Exception as e:
            logger.warning(f"Light OCR échoué: {e}")
            return _empty_result()

    # ── Read from full image + bounding boxes ─────────────────────────────────

    def read_from_detections(
        self,
        image: np.ndarray,
        detections: list[dict],
        padding: int = 10,
    ) -> list[dict]:
        """
        Iterate over YOLO detections and run OCR on each crop.

        Strategy:
          - YOLO detects two classes: 'container' (whole box) and 'texte' (text strip).
          - 'texte' crops are small and precise — OCR them first.
          - Only fall back to 'container' crops when no 'texte' detection exists.
          - NEVER merge 'texte' boxes into 'container' boxes.
          - Same-class boxes that overlap are still merged together.
        """
        h, w = image.shape[:2]

        if not detections:
            return []

        # ── Step 1: Split detections by class ──────────────────────────────────
        texte_dets     = [d for d in detections if d.get("class", "").lower() == "texte"]
        container_dets = [d for d in detections if d.get("class", "").lower() != "texte"]

        logger.info(f"{len(detections)} YOLO boxes: "
                    f"{len(texte_dets)} 'texte' + {len(container_dets)} 'container'")

        # ── Step 2: Choose which detections to OCR ─────────────────────────────
        dets_to_ocr = texte_dets if texte_dets else container_dets
        source_label = "texte" if texte_dets else "container"

        # Merge same-class overlapping boxes
        merged_boxes = self._merge_bounding_boxes(dets_to_ocr, h, w)
        logger.info(f"Using {source_label} detections: "
                    f"{len(dets_to_ocr)} boxes → {len(merged_boxes)} merged regions")

        ocr_results = []

        # ── Step 3: OCR on each merged region ──────────────────────────────────
        for merged in merged_boxes:
            x1, y1, x2, y2 = merged["bbox"]
            pad = 8 if texte_dets else max(padding, 20)
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(w, x2 + pad)
            y2 = min(h, y2 + pad)

            crop       = image[y1:y2, x1:x2]
            yolo_class = merged.get("class", "container")

            # Determine orientation from aspect ratio of the crop
            ch, cw = crop.shape[:2]
            orient_hint = "vertical" if ch > cw * 1.2 else "horizontal"
            logger.info(f"Crop: class='{yolo_class}' shape={cw}x{ch} → orient={orient_hint}")

            result = self.read_from_crop(crop, yolo_class=orient_hint)
            result["bbox"]            = merged["bbox"]
            result["yolo_confidence"] = merged.get("confidence", 0.0)
            result["class"]           = yolo_class
            ocr_results.append(result)

        # ── Step 4: If no ID found, retry on container crops ───────────────────
        found_any_id = any(r.get("container_id") for r in ocr_results)

        if not found_any_id and texte_dets and container_dets:
            logger.warning("No ID from texte crops — retrying on container crops...")
            merged_containers = self._merge_bounding_boxes(container_dets, h, w)
            for merged in merged_containers:
                x1, y1, x2, y2 = merged["bbox"]
                pad = max(padding, 20)
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)
                crop = image[y1:y2, x1:x2]
                ch, cw = crop.shape[:2]
                orient_hint = "vertical" if ch > cw * 1.2 else "horizontal"
                result = self.read_from_crop(crop, yolo_class=orient_hint)
                result["bbox"]            = merged["bbox"]
                result["yolo_confidence"] = merged.get("confidence", 0.0)
                result["class"]           = merged.get("class", "container")
                if result.get("container_id"):
                    ocr_results = [result]
                    logger.info(f"[OK] Container fallback found: {result['container_id']}")
                    found_any_id = True
                    break

        # ── Step 5: Last resort — full image OCR ──────────────────────────────
        if not found_any_id and detections:
            logger.warning("No ID from any crop — trying full image OCR fallback...")
            full_result = self.read_from_crop_light(image)
            if full_result.get("container_id"):
                full_result["bbox"]            = [0, 0, w, h]
                full_result["yolo_confidence"] = max(d.get("confidence", 0) for d in detections)
                full_result["class"]           = "full_image_fallback"
                ocr_results = [full_result]
                logger.info(f"[OK] Full image fallback found: {full_result['container_id']}")

        return ocr_results

    # ── Merge overlapping bounding boxes ───────────────────────────────────────

    @staticmethod
    def _merge_bounding_boxes(detections: list[dict], img_h: int, img_w: int) -> list[dict]:
        """
        Merge overlapping or nearby YOLO bounding boxes into larger regions.
        Only merges boxes of the same class.
        """
        if not detections:
            return []

        sorted_dets = sorted(detections, key=lambda d: d["bbox"][1])

        merged = []
        current = {
            "bbox": list(sorted_dets[0]["bbox"]),
            "confidence": sorted_dets[0].get("confidence", 0.0),
            "class": sorted_dets[0].get("class", "container"),
        }

        for det in sorted_dets[1:]:
            cx1, cy1, cx2, cy2 = current["bbox"]
            dx1, dy1, dx2, dy2 = det["bbox"]

            overlap_x = cx1 <= dx2 + 50 and dx1 <= cx2 + 50
            overlap_y = cy1 <= dy2 + 50 and dy1 <= cy2 + 50

            if overlap_x and overlap_y:
                current["bbox"] = [
                    min(cx1, dx1),
                    min(cy1, dy1),
                    max(cx2, dx2),
                    max(cy2, dy2),
                ]
                current["confidence"] = max(current["confidence"],
                                            det.get("confidence", 0.0))
            else:
                merged.append(current)
                current = {
                    "bbox": list(det["bbox"]),
                    "confidence": det.get("confidence", 0.0),
                    "class": det.get("class", "container"),
                }

        merged.append(current)
        return merged

    # ── Container ID extractor ────────────────────────────────────────────────

    @staticmethod
    def _extract_container_id(text: str) -> Optional[str]:
        """
        Extract a valid ISO 6346 container ID from OCR text.
        Applies character substitution to fix common OCR misreads.
        """
        # Clean text to only alphanumeric
        text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())

        # Container IDs are usually 11 chars. Scan for 10-11 long alphanumeric chunks
        matches = re.finditer(r'[A-Z0-9]{10,11}', text_clean)
        for m in matches:
            candidate = m.group(0)

            # First 4 chars must be letters — fix common digit→letter substitutions
            prefix = candidate[:4]
            prefix = prefix.replace('0', 'O').replace('1', 'I').replace('5', 'S').replace('8', 'B')

            # Remaining chars must be digits — fix common letter→digit substitutions
            suffix = candidate[4:]
            suffix = suffix.replace('O', '0').replace('I', '1').replace('S', '5').replace('B', '8').replace('Z', '7').replace('G', '6').replace('D', '0')

            fixed = prefix + suffix
            if re.match(r'^[A-Z]{4}\d{6,7}$', fixed):
                return fixed

        # Strict fallback: use the original regex on cleaned text
        match = CONTAINER_ID_PATTERN.search(text_clean)
        if match:
            return match.group(0)

        fallback = re.search(r"[A-Z]{4}\d{6,7}", text_clean)
        return fallback.group(0) if fallback else None

    @staticmethod
    def _empty_result() -> dict:
        return _empty_result()


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        image = cv2.imread(img_path)
        if image is None:
            print(f"Error: Cannot read image '{img_path}'")
            sys.exit(1)
        reader = OCRReader()
        result = reader.read_from_crop(image)
        print(json.dumps(result, indent=2))
    else:
        # Test process_image with a file
        print("Usage: python ocr_reader.py <image_path>")
        print("   or: provide image bytes via process_image()")
        sys.exit(1)
