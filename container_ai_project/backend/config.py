"""
Backend Configuration
Loads all settings from .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ── Flask ──────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
FLASK_ENV  = os.getenv("FLASK_ENV", "development")
DEBUG      = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# ── Database ───────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/database/marsa_maroc.db")

# ── Paths ──────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER  = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
STATIC_FOLDER  = BASE_DIR / os.getenv("STATIC_FOLDER", "static")
REPORTS_FOLDER = BASE_DIR / os.getenv("REPORTS_FOLDER", "reports")

# Make sure directories exist
for folder in [UPLOAD_FOLDER, STATIC_FOLDER, REPORTS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# ── YOLO ───────────────────────────────────────────────────────────────────────
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "model/yolov8n.pt")
YOLO_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.40"))

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_BACKEND    = os.getenv("LLM_BACKEND", "template")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "mistral:7b")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
