"""
Flask Blueprint: /yard/*
═══════════════════════════════════════════════════════════════════
GET  /yard/view      → serves the Three.js 3-D visualiser page
GET  /yard/state     → returns full yard JSON for the front-end
POST /yard/optimize  → find best slot for a new container (EDD + SA)
POST /yard/place     → commit a container to a confirmed slot
DELETE /yard/reset   → reset the in-memory yard to the demo state
"""
from __future__ import annotations

import json
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory, current_app

# ── Lazy-import the optimizer so Flask starts even if something is wrong ───────
from services.yard_optimizer import (
    Container,
    Yard,
    build_demo_yard,
    find_best_slot,
    get_yard_state_dict,
)

yard_bp = Blueprint("yard", __name__, url_prefix="/yard")

# ── In-memory yard singleton ───────────────────────────────────────────────────
# Shared across all requests in the same Flask worker process.
_yard: Yard = build_demo_yard()


def _get_yard() -> Yard:
    return _yard


# ─────────────────────────────────────────────────────────────────────────────
# GET /yard/view  — serve the Three.js HTML page
# ─────────────────────────────────────────────────────────────────────────────
@yard_bp.route("/view", methods=["GET"])
def yard_view():
    """
    Serve the standalone Three.js yard visualiser.
    The HTML file lives at  <project_root>/static/yard_view.html
    """
    try:
        # Try config path first
        static_folder = current_app.static_folder or str(
            Path(__file__).resolve().parents[2] / "static"
        )
        return send_from_directory(static_folder, "yard_view.html")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET /yard/state  — return full yard as JSON
# ─────────────────────────────────────────────────────────────────────────────
@yard_bp.route("/state", methods=["GET"])
def yard_state():
    """
    Return the complete yard state as JSON.
    Used by the Three.js page to render the 3-D yard on load / refresh.
    """
    yard = _get_yard()
    return jsonify(get_yard_state_dict(yard))


# ─────────────────────────────────────────────────────────────────────────────
# POST /yard/optimize  — find the best slot for a container
# ─────────────────────────────────────────────────────────────────────────────
@yard_bp.route("/optimize", methods=["POST"])
def yard_optimize():
    """
    Body (JSON):
    {
        "container_id":   "MSCU999",      required
        "size":           20,             required — 20 or 40
        "weight":         25000,          required — kg
        "departure_time": "2026-05-10"    required — ISO date string
    }

    Returns the recommended slot + EDD reasoning.
    """
    data = request.get_json(force=True, silent=True) or {}

    if "container_id" not in data:
        return jsonify({"error": "Missing field: container_id"}), 400

    cid = str(data["container_id"])
    
    # Try fetching details from manifest
    from services.db_manager import get_manifest_container
    manifest_info = get_manifest_container(cid)
    
    size = int(data.get("size", 20))
    weight = float(data.get("weight", 25000))
    departure_time = str(data.get("departure_time", "2026-05-10"))
    
    if manifest_info:
        size = int(manifest_info.get("size", size))
        weight = float(manifest_info.get("weight", weight))
        departure_time = str(manifest_info.get("departure_time", departure_time))

    try:
        container = Container(
            id=cid,
            size=size,
            weight=weight,
            departure_time=departure_time,
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400

    if container.size not in (20, 40):
        return jsonify({"error": "size must be 20 or 40"}), 400

    yard = _get_yard()

    # ── Run optimizer ─────────────────────────────────────────────────────────
    result = find_best_slot(container, yard)

    if result is None:
        return jsonify({
            "success": False,
            "message": "Yard is full — no valid slot found for this container.",
        }), 200

    (block_id, slot), cost, stage_label = result

    # Build a human-readable EDD explanation
    edd_explanation = (
        f"Container '{container.id}' (departure {container.departure_time}) was "
        f"placed at {slot.localization} (tier {slot.tier}) in block {block_id}. "
        f"The EDD rule verified that no container with an earlier departure date "
        f"sits below this position, eliminating the need for costly re-handles "
        f"when loading vessels. Placement resolved via {stage_label}."
    )

    return jsonify({
        "success":       True,
        "container_id":  container.id,
        "block":         block_id,
        "bay":           slot.bay,
        "row":           slot.row,
        "tier":          slot.tier,
        "localization":  slot.localization,
        "optimizer_cost": round(cost, 3),
        "stage":         stage_label,
        "edd_explanation": edd_explanation,
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /yard/place  — commit a container to the yard
# ─────────────────────────────────────────────────────────────────────────────
@yard_bp.route("/place", methods=["POST"])
def yard_place():
    """
    Body (JSON):
    {
        "container_id":   "MSCU999",
        "size":           20,
        "weight":         25000,
        "departure_time": "2026-05-10",
        "block":          "A",
        "bay":            0,
        "row":            1
    }

    Actually places the container in the in-memory yard and returns
    the updated yard state. Call /yard/optimize first to get suggested
    block/bay/row, then confirm with this endpoint.
    """
    data = request.get_json(force=True, silent=True) or {}
    required = ("container_id", "block", "bay", "row")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    cid = str(data["container_id"])
    
    from services.db_manager import get_manifest_container
    manifest_info = get_manifest_container(cid)
    
    size = int(data.get("size", 20))
    weight = float(data.get("weight", 25000))
    departure_time = str(data.get("departure_time", "2026-05-10"))
    
    if manifest_info:
        size = int(manifest_info.get("size", size))
        weight = float(manifest_info.get("weight", weight))
        departure_time = str(manifest_info.get("departure_time", departure_time))

    try:
        container = Container(
            id=cid,
            size=size,
            weight=weight,
            departure_time=departure_time,
        )
        block_id = str(data["block"])
        bay      = int(data["bay"])
        row      = int(data["row"])
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400

    yard = _get_yard()
    placed_slot = yard.place_container(block_id, bay, row, container)

    if placed_slot is None:
        return jsonify({"error": "Could not place container — slot may be full or block not found."}), 400

    return jsonify({
        "success":      True,
        "container_id": container.id,
        "localization": placed_slot.localization,
        "tier":         placed_slot.tier,
        "yard_state":   get_yard_state_dict(yard),
    })


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /yard/reset  — reset yard to demo state
# ─────────────────────────────────────────────────────────────────────────────
@yard_bp.route("/reset", methods=["DELETE"])
def yard_reset():
    """Reset the in-memory yard to the pre-seeded demo state."""
    global _yard
    _yard = build_demo_yard()
    return jsonify({"success": True, "message": "Yard reset to demo state."})
