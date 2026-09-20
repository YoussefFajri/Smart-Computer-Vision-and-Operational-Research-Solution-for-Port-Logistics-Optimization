"""
Database Manager — SQLAlchemy ORM
Handles all DB interactions for the containers table.
Supports SQLite (dev) and PostgreSQL (prod) via DATABASE_URL.
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, func, desc
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ── ORM Base ──────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class Container(Base):
    __tablename__ = "containers"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    container_id     = Column(String(50))
    date_detection   = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    ship_name        = Column(String(100))
    dock_name        = Column(String(100))
    sts_operator     = Column(String(100))
    status           = Column(String(50), default="détecté")
    image_path       = Column(String(255))
    annotated_path   = Column(String(255))
    ocr_text         = Column(Text)
    ocr_confidence   = Column(Float)
    processing_time  = Column(Float)
    notes            = Column(Text)
    
    # ── Yard Placement ──
    yard_block        = Column(String(10), nullable=True)
    yard_localization = Column(String(50), nullable=True)
    yard_tier         = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "container_id":     self.container_id,
            "date_detection":   self.date_detection.isoformat() if self.date_detection else None,
            "confidence_score": self.confidence_score,
            "ship_name":        self.ship_name,
            "dock_name":        self.dock_name,
            "sts_operator":     self.sts_operator,
            "status":           self.status,
            "image_path":       self.image_path,
            "annotated_path":   self.annotated_path,
            "ocr_text":         self.ocr_text,
            "ocr_confidence":   self.ocr_confidence,
            "processing_time":  self.processing_time,
            "notes":            self.notes,
            "yard_block":       self.yard_block,
            "yard_localization": self.yard_localization,
            "yard_tier":        self.yard_tier,
        }


class ManifestContainer(Base):
    __tablename__ = "manifests"

    container_id   = Column(String(50), primary_key=True)
    size           = Column(Integer)
    weight         = Column(Float)
    departure_time = Column(String(50))
    
    # Pre-planned yard placement
    yard_block        = Column(String(10), nullable=True)
    yard_localization = Column(String(50), nullable=True)
    yard_tier         = Column(Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            "container_id":   self.container_id,
            "size":           self.size,
            "weight":         self.weight,
            "departure_time": self.departure_time,
            "yard_block":       self.yard_block,
            "yard_localization": self.yard_localization,
            "yard_tier":        self.yard_tier,
        }


class DetectionSession(Base):
    __tablename__ = "sessions"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    session_date   = Column(DateTime, default=datetime.utcnow)
    ship_name      = Column(String(100))
    dock_name      = Column(String(100))
    sts_operator   = Column(String(100))
    total_detected = Column(Integer, default=0)
    total_unloaded = Column(Integer, default=0)
    ocr_errors     = Column(Integer, default=0)
    report_path    = Column(String(255))


# ── Engine & Session Factory (lazy init) ───────────────────────────────────────
_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        # Re-read config so the absolute path from .env is used
        try:
            from backend.config import DATABASE_URL as _db_url
        except ImportError:
            from config import DATABASE_URL as _db_url

        kwargs = {"check_same_thread": False} if "sqlite" in _db_url else {}
        _engine = create_engine(_db_url, echo=False, connect_args=kwargs)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine, _SessionLocal


def SessionLocal():
    """Return a new DB session. Use as: with SessionLocal() as db:"""
    _, SL = _get_engine()
    return SL()


def init_db():
    """Create all tables if they don't exist."""
    engine, _ = _get_engine()
    Base.metadata.create_all(bind=engine)


# ── CRUD helpers ───────────────────────────────────────────────────────────────
def save_container(data: dict) -> Container:
    with SessionLocal() as db:
        # Avoid creating duplicate entries for the exact same detection ID/timestamp if needed, 
        # but for now we trust the input data dict maps cleanly.
        obj = Container(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


def save_manifest_containers(records: list[dict]) -> int:
    """Save a list of manifest records. Clears old manifest first for simplicity."""
    with SessionLocal() as db:
        db.query(ManifestContainer).delete()
        objects = [ManifestContainer(**r) for r in records]
        db.add_all(objects)
        db.commit()
        return len(objects)


def get_manifest_container(container_id: str) -> Optional[dict]:
    """Retrieve manifest info for a given container ID."""
    with SessionLocal() as db:
        row = db.query(ManifestContainer).filter_by(container_id=container_id).first()
        return row.to_dict() if row else None


def get_all_containers(limit: int = 500, offset: int = 0) -> list[dict]:
    with SessionLocal() as db:
        rows = (db.query(Container)
                  .order_by(desc(Container.date_detection))
                  .offset(offset).limit(limit).all())
        return [r.to_dict() for r in rows]


def get_container_by_id(record_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        row = db.get(Container, record_id)
        return row.to_dict() if row else None


def get_stats() -> dict:
    with SessionLocal() as db:
        total = db.query(func.count(Container.id)).scalar() or 0
        unloaded = (db.query(func.count(Container.id))
                      .filter(Container.status == "déchargé").scalar() or 0)
        ocr_errors = (db.query(func.count(Container.id))
                        .filter(Container.container_id == None).scalar() or 0)  # noqa: E711
        avg_conf = db.query(func.avg(Container.confidence_score)).scalar() or 0.0
        avg_time = db.query(func.avg(Container.processing_time)).scalar() or 0.0

        # Ops per day (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent = (db.query(func.date(Container.date_detection),
                           func.count(Container.id))
                    .filter(Container.date_detection >= seven_days_ago)
                    .group_by(func.date(Container.date_detection))
                    .all())
        ops_by_day = {str(r[0]): r[1] for r in recent}

        return {
            "total":           total,
            "unloaded":        unloaded,
            "ocr_errors":      ocr_errors,
            "ocr_success_rate": round((total - ocr_errors) / max(total, 1) * 100, 1),
            "avg_confidence":  round(float(avg_conf) * 100, 1),
            "avg_processing_time": round(float(avg_time), 2),
            "ops_by_day":      ops_by_day,
        }


def get_recent_containers(limit: int = 20) -> list[dict]:
    with SessionLocal() as db:
        rows = (db.query(Container)
                  .order_by(desc(Container.date_detection))
                  .limit(limit).all())
        return [r.to_dict() for r in rows]


def get_decharge_containers(limit: int = 50) -> list[dict]:
    """Return containers with status 'déchargé' (successfully identified via OCR)."""
    with SessionLocal() as db:
        rows = (db.query(Container)
                  .filter(Container.status == "déchargé")
                  .order_by(desc(Container.date_detection))
                  .limit(limit).all())
        return [r.to_dict() for r in rows]
