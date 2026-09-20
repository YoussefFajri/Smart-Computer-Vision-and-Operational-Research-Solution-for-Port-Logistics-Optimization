"""
Flask Route: GET /stats
Returns aggregated statistics for the dashboard.
"""
from __future__ import annotations

from flask import Blueprint, jsonify

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats", methods=["GET"])
def get_stats():
    """GET /stats — Dashboard KPIs"""
    from services.db_manager import get_stats
    data = get_stats()
    return jsonify(data)
