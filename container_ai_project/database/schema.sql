"""
Database Schema — SQLite (dev) / PostgreSQL (prod)
Initialise automatically on first launch via SQLAlchemy.
"""

# ── SQLAlchemy DDL equivalent (also kept as raw SQL for reference) ─────────────
SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS containers (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    container_id     TEXT,
    date_detection   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL,
    ship_name        TEXT,
    dock_name        TEXT,
    sts_operator     TEXT,
    status           TEXT DEFAULT 'détecté',
    image_path       TEXT,
    annotated_path   TEXT,
    ocr_text         TEXT,
    ocr_confidence   REAL,
    processing_time  REAL,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ship_name       TEXT,
    dock_name       TEXT,
    sts_operator    TEXT,
    total_detected  INTEGER DEFAULT 0,
    total_unloaded  INTEGER DEFAULT 0,
    ocr_errors      INTEGER DEFAULT 0,
    report_path     TEXT
);
"""
