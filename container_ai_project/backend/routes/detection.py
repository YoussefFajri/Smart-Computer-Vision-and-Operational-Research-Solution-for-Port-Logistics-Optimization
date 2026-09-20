"""
Flask Route: POST /detect
Receives an image → runs YOLO → OCR → saves to DB → returns JSON.
"""
from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import UPLOAD_FOLDER, STATIC_FOLDER, YOLO_MODEL_PATH, YOLO_CONFIDENCE, ALLOWED_EXTENSIONS

detect_bp = Blueprint("detect", __name__)

# Lazy-loaded singletons
_detector = None
_ocr_reader = None


def _get_detector():
    global _detector
    if _detector is None:
        from model.container_detector import ContainerDetector
        _detector = ContainerDetector(
            model_path=str(Path(__file__).resolve().parents[2] / YOLO_MODEL_PATH),
            confidence=YOLO_CONFIDENCE,
        )
    return _detector


def _get_ocr():
    global _ocr_reader
    if _ocr_reader is None:
        from services.ocr_reader import OCRReader
        _ocr_reader = OCRReader()
    return _ocr_reader


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@detect_bp.route("/detect", methods=["POST"])
def detect():
    """
    POST /detect
    Form data:
      - file:         image file (required)
      - ship_name:    str (optional)
      - dock_name:    str (optional)
      - sts_operator: str (optional)
    """
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    f = request.files["file"]
    if not f.filename or not _allowed(f.filename):
        return jsonify({"error": "Format de fichier non supporté"}), 400

    # ── Save uploaded image ────────────────────────────────────────────────────
    sid      = uuid.uuid4().hex[:10]
    ext      = Path(f.filename).suffix.lower()
    filename = f"upload_{sid}{ext}"
    img_path = UPLOAD_FOLDER / filename
    f.save(str(img_path))

    # ── Read session metadata ──────────────────────────────────────────────────
    ship     = request.form.get("ship_name", "")
    dock     = request.form.get("dock_name", "")
    operator = request.form.get("sts_operator", "")

    # ── YOLO detection ─────────────────────────────────────────────────────────
    t0      = time.perf_counter()
    detector = _get_detector()
    image    = cv2.imread(str(img_path))

    det_result = detector.detect(
        image_source=image,
        save_dir=STATIC_FOLDER,
        session_id=sid,
    )

    # ── OCR ────────────────────────────────────────────────────────────────────
    ocr_reader  = _get_ocr()
    ocr_results = ocr_reader.read_from_detections(image, det_result["detections"])

    # ── Save to DB & Verification ───────────────────────────────────────────────
    from services.db_manager import save_container, get_manifest_container

    saved_ids = []

    for ocr in ocr_results:
        cid = ocr.get("container_id")
        status = "déchargé" if cid else "détecté"
        db_data = {
            "container_id":     cid,
            "confidence_score": ocr.get("yolo_confidence"),
            "ship_name":        ship,
            "dock_name":        dock,
            "sts_operator":     operator,
            "status":           status,
            "image_path":       str(img_path),
            "annotated_path":   det_result["annotated_path"],
            "ocr_text":         ocr.get("raw_text"),
            "ocr_confidence":   ocr.get("ocr_confidence"),
            "processing_time":  det_result["processing_time"],
        }

        # Verification logic
        if cid:
            manifest_info = get_manifest_container(cid)
            if manifest_info:
                db_data["status"] = "vérifié"
                # Link to the pre-planned location
                db_data["yard_block"] = manifest_info.get("yard_block")
                db_data["yard_localization"] = manifest_info.get("yard_localization")
                db_data["yard_tier"] = manifest_info.get("yard_tier")
                db_data["notes"] = "ID vérifié avec le manifeste et lié à l'emplacement planifié."
            else:
                db_data["status"] = "non-planifié"
                db_data["notes"] = "ID non trouvé dans le manifeste - attention requise"

        record = save_container(db_data)
        saved_ids.append(record.id)

    total_time = round(time.perf_counter() - t0, 3)

    return jsonify({
        "success":         True,
        "session_id":      sid,
        "total_detected":  len(det_result["detections"]),
        "containers":      ocr_results,
        "annotated_image": det_result["annotated_path"],
        "processing_time": total_time,
        "db_ids":          saved_ids,
    })
