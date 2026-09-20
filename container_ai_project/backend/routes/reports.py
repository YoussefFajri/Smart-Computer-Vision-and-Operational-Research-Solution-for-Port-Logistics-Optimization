"""
Flask Route: GET /report/pdf
Generates and streams a PDF report.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Blueprint, send_file, jsonify, request
import io

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/report/pdf", methods=["GET"])
def generate_report():
    """
    GET /report/pdf
    Optional query params:
      ship_name, dock_name, sts_operator
    """
    try:
        from services.db_manager import get_stats, get_all_containers
        from services.report_gen import generate_pdf

        stats      = get_stats()
        containers = get_all_containers(limit=200)

        # Enrich stats with session + container list
        stats["ship_name"]    = request.args.get("ship_name", "—")
        stats["dock_name"]    = request.args.get("dock_name", "—")
        stats["sts_operator"] = request.args.get("sts_operator", "—")
        stats["containers"]   = containers

        # LLM summary
        llm_summary = None
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "llm"))
            from llm_report import generate_summary
            anomalies = [c.get("container_id", "") or "" for c in containers if not c.get("container_id")]
            llm_summary = generate_summary({
                "total_containers":    stats.get("total", 0),
                "unloaded":            stats.get("unloaded", 0),
                "ocr_errors":          stats.get("ocr_errors", 0),
                "dock_name":           stats["dock_name"],
                "sts_operator":        stats["sts_operator"],
                "ship_name":           stats["ship_name"],
                "anomalies":           anomalies,
                "avg_processing_time": stats.get("avg_processing_time", 0),
                "ocr_success_rate":    stats.get("ocr_success_rate", 100),
            })
        except Exception as e:
            print(f"[Report] LLM error: {e}")
            llm_summary = "Résumé automatique non disponible."

        pdf_bytes = generate_pdf(stats, llm_summary=llm_summary)

        fname = f"rapport_marsa_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=fname,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
