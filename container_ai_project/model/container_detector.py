"""
YOLOv8 Container Detector
─────────────────────────
Loads a YOLO model and runs inference on an image.
Returns bounding boxes, confidence scores, and an annotated image.
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


# ── Detector class ─────────────────────────────────────────────────────────────
class ContainerDetector:
    """
    Wraps YOLOv8 for container detection.

    Usage:
        detector = ContainerDetector("yolov8n.pt")
        results  = detector.detect("port_image.jpg")
    """

    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.40):
        self.model_path = model_path
        self.confidence = confidence
        print(f"[YOLO] Loading model: {model_path}")
        self.model = YOLO(model_path)
        print("[YOLO] Model ready.")

    # ── Main detection method ──────────────────────────────────────────────────
    def detect(
        self,
        image_source: str | np.ndarray,
        save_dir: str | Path = "static",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run detection on an image.

        Args:
            image_source: Path to image file OR numpy BGR array.
            save_dir:     Where to save the annotated image.
            session_id:   Optional tag for the output filename.

        Returns:
            {
              "detections": [
                  {"bbox": [x1,y1,x2,y2], "confidence": float, "class": str}
              ],
              "annotated_path": str,   # path to saved annotated image
              "processing_time": float # seconds
            }
        """
        t0 = time.perf_counter()
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # ── Load image ─────────────────────────────────────────────────────────
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                raise ValueError(f"Cannot read image: {image_source}")
        else:
            image = image_source.copy()

        # ── Run inference ──────────────────────────────────────────────────────
        results = self.model.predict(
            source=image,
            conf=self.confidence,
            verbose=False,
        )

        # ── Parse results ──────────────────────────────────────────────────────
        detections = []
        annotated  = image.copy()

        if results and len(results) > 0:
            result = results[0]
            boxes  = result.boxes

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf  = float(box.conf[0])
                cls   = int(box.cls[0])
                label = self.model.names.get(cls, "container")

                detections.append({
                    "bbox":       [x1, y1, x2, y2],
                    "confidence": round(conf, 4),
                    "class":      label,
                })

                # Draw bounding box
                color = (0, 200, 100)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated,
                    f"{label} {conf:.0%}",
                    (x1, max(y1 - 6, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2,
                )

        # ── Save annotated image ───────────────────────────────────────────────
        sid   = session_id or uuid.uuid4().hex[:8]
        fname = f"annotated_{sid}.jpg"
        fpath = save_dir / fname
        cv2.imwrite(str(fpath), annotated)

        elapsed = round(time.perf_counter() - t0, 3)
        return {
            "detections":      detections,
            "annotated_path":  str(fpath),
            "processing_time": elapsed,
        }

    # ── Crop helper ───────────────────────────────────────────────────────────
    @staticmethod
    def crop_region(image: np.ndarray, bbox: list[int], padding: int = 10) -> np.ndarray:
        """Return a padded crop of the bounding-box region."""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = bbox
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        return image[y1:y2, x1:x2]


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, json
    img = sys.argv[1] if len(sys.argv) > 1 else None
    if not img:
        print("Usage: python container_detector.py <image_path>")
        sys.exit(1)

    det = ContainerDetector()
    out = det.detect(img)
    print(json.dumps(out, indent=2))
    print(f"\n✅  Found {len(out['detections'])} object(s) in {out['processing_time']}s")
    print(f"   Annotated image saved → {out['annotated_path']}")
