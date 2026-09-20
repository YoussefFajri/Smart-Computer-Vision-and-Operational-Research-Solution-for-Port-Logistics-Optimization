"""
Flask Route: POST /manifest/upload
Upload a CSV manifest containing container data (ID, size, weight, departure).
"""
from __future__ import annotations

import csv
import io
from flask import Blueprint, request, jsonify

from services.db_manager import save_manifest_containers
from services.yard_optimizer import Container as YardContainer, find_best_slot
from routes.yard import _get_yard

manifest_bp = Blueprint("manifest", __name__, url_prefix="/manifest")

@manifest_bp.route("/upload", methods=["POST"])
def upload_manifest():
    """
    POST /manifest/upload
    Expects a multipart/form-data request with a file named 'file'.
    The CSV should have headers: container_id, size, weight, departure_time
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("utf8"), newline=None)
        reader = csv.DictReader(stream)
        
        # Verify required headers
        required_fields = {"container_id", "size", "weight", "departure_time"}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            return jsonify({
                "error": f"CSV must contain headers: {', '.join(required_fields)}"
            }), 400

        records = []
        for row in reader:
            if not row["container_id"]:
                continue
            
            try:
                records.append({
                    "container_id":   str(row["container_id"]).strip(),
                    "size":           int(row["size"]),
                    "weight":         float(row["weight"]),
                    "departure_time": str(row["departure_time"]).strip(),
                })
            except (ValueError, TypeError) as e:
                # Skip rows with malformed data or log them
                pass
                
        if not records:
            return jsonify({"error": "No valid data found in CSV"}), 400

        # Sort records by departure_time DESC (latest first)
        # This guarantees EDD: latest depart first (bottom), earliest depart last (top)
        records.sort(key=lambda x: x["departure_time"], reverse=True)

        # Pre-plan yard
        yard = _get_yard()
        yard.reset()
        
        for record in records:
            y_ctr = YardContainer(
                id=record["container_id"],
                size=record["size"],
                weight=record["weight"],
                departure_time=record["departure_time"]
            )
            opt_result = find_best_slot(y_ctr, yard)
            if opt_result:
                (block_id, slot), cost, stage_label = opt_result
                placed_slot = yard.place_container(block_id, slot.bay, slot.row, y_ctr)
                if placed_slot:
                    record["yard_block"] = block_id
                    record["yard_localization"] = placed_slot.localization
                    record["yard_tier"] = placed_slot.tier
            else:
                record["yard_block"] = None
                record["yard_localization"] = None
                record["yard_tier"] = None

        saved_count = save_manifest_containers(records)
        
        return jsonify({
            "success": True, 
            "message": f"Successfully planned and loaded {saved_count} containers from manifest."
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500
