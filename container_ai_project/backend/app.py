"""
Flask Application — Port Logistics AI
Entry point for the backend REST API.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── Path setup (so imports work from project root) ─────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "model"))

from flask import Flask, jsonify
from flask_cors import CORS

import config as cfg
from services.db_manager import init_db

# ── Blueprints ─────────────────────────────────────────────────────────────────
from routes.detection  import detect_bp
from routes.containers import containers_bp
from routes.stats      import stats_bp
from routes.reports    import reports_bp
from routes.yard       import yard_bp
from routes.manifest   import manifest_bp

# ── App factory ────────────────────────────────────────────────────────────────
def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(cfg.STATIC_FOLDER))
    app.config["SECRET_KEY"]         = cfg.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = cfg.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"]      = str(cfg.UPLOAD_FOLDER)

    CORS(app, origins="*")

    # Blueprints
    app.register_blueprint(detect_bp)
    app.register_blueprint(containers_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(yard_bp)
    app.register_blueprint(manifest_bp)

    # Health-check
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "Port Logistics AI"})

    # Serve annotated images
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        from flask import send_from_directory
        return send_from_directory(cfg.STATIC_FOLDER, filename)

    return app


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  [*] Port Logistics AI -- Flask API")
    print("=" * 55)
    print(f"  Database : {cfg.DATABASE_URL}")
    print(f"  Uploads  : {cfg.UPLOAD_FOLDER}")
    print(f"  Model    : {cfg.YOLO_MODEL_PATH}")
    print("=" * 55)

    # Initialise DB tables
    init_db()
    print("  [OK] Database initialised")

    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=cfg.DEBUG)
