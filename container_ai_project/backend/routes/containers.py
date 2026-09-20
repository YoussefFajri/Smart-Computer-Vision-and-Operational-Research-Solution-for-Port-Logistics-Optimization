"""
Flask Route: GET /containers, GET /container/<id>
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

containers_bp = Blueprint("containers", __name__)


@containers_bp.route("/containers", methods=["GET"])
def list_containers():
    """GET /containers?limit=100&offset=0"""
    from services.db_manager import get_all_containers
    limit  = int(request.args.get("limit", 200))
    offset = int(request.args.get("offset", 0))
    data   = get_all_containers(limit=limit, offset=offset)
    return jsonify({"containers": data, "count": len(data)})


@containers_bp.route("/container/<int:record_id>", methods=["GET"])
def get_container(record_id: int):
    """GET /container/<id>"""
    from services.db_manager import get_container_by_id
    data = get_container_by_id(record_id)
    if not data:
        return jsonify({"error": "Conteneur non trouvé"}), 404
    return jsonify(data)


@containers_bp.route("/containers/decharge", methods=["GET"])
def list_decharge():
    """GET /containers/decharge?limit=50 — Containers with status 'déchargé'"""
    from services.db_manager import get_decharge_containers
    limit = int(request.args.get("limit", 50))
    data  = get_decharge_containers(limit=limit)
    return jsonify({"containers": data, "count": len(data)})
