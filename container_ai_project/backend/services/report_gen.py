"""
PDF Report Generator — ReportLab
─────────────────────────────────
Produces a professional bilingual (French) PDF report with:
  - Cover page with logo placeholder
  - Summary statistics table
  - Container ID list
  - Anomalies section
  - LLM-generated summary
  - Recommendations
"""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)

# ── Brand colors ───────────────────────────────────────────────────────────────
MARSA_BLUE  = colors.HexColor("#0B2B5E")
MARSA_GREEN = colors.HexColor("#E65100")
MARSA_LIGHT = colors.HexColor("#E8F4F8")
TEXT_DARK   = colors.HexColor("#1A1A2E")

# ── Style sheet ───────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "MarsaTitle",
    parent=styles["Title"],
    fontSize=22,
    textColor=MARSA_BLUE,
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)
SUBTITLE_STYLE = ParagraphStyle(
    "MarsaSubtitle",
    parent=styles["Normal"],
    fontSize=13,
    textColor=MARSA_GREEN,
    spaceAfter=4,
    alignment=TA_CENTER,
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=13,
    textColor=MARSA_BLUE,
    spaceBefore=14,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)
BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontSize=10,
    leading=16,
    textColor=TEXT_DARK,
    alignment=TA_JUSTIFY,
)
SMALL_STYLE = ParagraphStyle(
    "Small",
    parent=styles["Normal"],
    fontSize=8,
    textColor=colors.grey,
    alignment=TA_CENTER,
)


# ── Generator ─────────────────────────────────────────────────────────────────
def generate_pdf(
    data: dict,
    output_path: Optional[str] = None,
    llm_summary: Optional[str] = None,
) -> bytes:
    """
    Generate the PDF report.

    Args:
        data: Stats dict from db_manager.get_stats() enriched with session info.
        output_path: Optional file path to save PDF.
        llm_summary: Pre-generated LLM paragraph.

    Returns:
        Raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
        title="Rapport Opérationnel — Marsa Maroc",
        author="Port Logistics AI",
    )

    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "logo_Marsa_maroc.png")
        if os.path.exists(logo_path):
            img = Image(logo_path, width=5*cm, height=3*cm, kind='proportional')
            story.append(img)
            story.append(Spacer(1, 0.5 * cm))
    except Exception as e:
        print(f"Error loading logo for PDF: {e}")

    story.append(Paragraph("MARSA MAROC", TITLE_STYLE))
    story.append(Paragraph("Port de Casablanca — Terminal à Conteneurs", SUBTITLE_STYLE))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=MARSA_BLUE))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"<b>Rapport Opérationnel Journalier</b><br/>"
        f"Généré le {datetime.now().strftime('%d %B %Y à %H:%M')}",
        SUBTITLE_STYLE,
    ))
    story.append(Spacer(1, 1 * cm))

    # ── Session Information ────────────────────────────────────────────────────
    story.append(Paragraph("Informations de la session", SECTION_STYLE))
    session_data = [
        ["Navire", data.get("ship_name", "—")],
        ["Quai", data.get("dock_name", "—")],
        ["Responsable STS", data.get("sts_operator", "—")],
        ["Date", datetime.now().strftime("%d/%m/%Y")],
    ]
    story.append(_info_table(session_data))

    # ── Statistics ────────────────────────────────────────────────────────────
    story.append(Paragraph("Statistiques de la session", SECTION_STYLE))
    stats = [
        ["Indicateur", "Valeur"],
        ["Total conteneurs détectés", str(data.get("total", 0))],
        ["Conteneurs déchargés", str(data.get("unloaded", 0))],
        ["Erreurs OCR", str(data.get("ocr_errors", 0))],
        ["Taux de réussite OCR", f"{data.get('ocr_success_rate', 0):.1f}%"],
        ["Confiance YOLO moyenne", f"{data.get('avg_confidence', 0):.1f}%"],
        ["Temps de traitement moyen", f"{data.get('avg_processing_time', 0):.2f}s"],
    ]
    story.append(_stats_table(stats))

    # ── Container ID list ─────────────────────────────────────────────────────
    containers = data.get("containers", [])
    if containers:
        story.append(Paragraph("Liste des conteneurs détectés", SECTION_STYLE))
        rows = [["#", "ID Conteneur", "Confiance", "Statut", "Heure"]]
        for i, c in enumerate(containers[:60], 1):
            rows.append([
                str(i),
                c.get("container_id") or "Illisible",
                f"{(c.get('confidence_score') or 0) * 100:.0f}%",
                c.get("status", "—"),
                str(c.get("date_detection", ""))[:16],
            ])
        story.append(_container_table(rows))

    # ── Anomalies ─────────────────────────────────────────────────────────────
    anomalies = [c for c in containers if not c.get("container_id")]
    story.append(Paragraph("Anomalies & Identifiants illisibles", SECTION_STYLE))
    if anomalies:
        anom_text = f"{len(anomalies)} conteneur(s) avec OCR échoué nécessitent une vérification manuelle."
        story.append(Paragraph(anom_text, BODY_STYLE))
    else:
        story.append(Paragraph("Aucune anomalie détectée. Tous les identifiants ont été lus correctement.", BODY_STYLE))

    # ── LLM Summary ───────────────────────────────────────────────────────────
    story.append(Paragraph("Résumé opérationnel (IA)", SECTION_STYLE))
    summary_text = llm_summary or "Résumé non disponible."
    story.append(Paragraph(summary_text, BODY_STYLE))

    # ── Recommendations ───────────────────────────────────────────────────────
    story.append(Paragraph("Recommandations", SECTION_STYLE))
    reco_items = _build_recommendations(data)
    for item in reco_items:
        story.append(Paragraph(f"• {item}", BODY_STYLE))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph(
        "Document généré automatiquement par le système Port Logistics AI — Marsa Maroc.",
        SMALL_STYLE,
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


# ── Helpers ───────────────────────────────────────────────────────────────────
def _info_table(rows: list) -> Table:
    t = Table(rows, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), MARSA_LIGHT),
        ("TEXTCOLOR",   (0, 0), (0, -1), MARSA_BLUE),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, MARSA_LIGHT]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _stats_table(rows: list) -> Table:
    t = Table(rows, colWidths=[10 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), MARSA_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, MARSA_LIGHT]),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _container_table(rows: list) -> Table:
    t = Table(rows, colWidths=[1 * cm, 5 * cm, 3 * cm, 4 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), MARSA_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, MARSA_LIGHT]),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _build_recommendations(data: dict) -> list[str]:
    recs = []
    ocr_rate = data.get("ocr_success_rate", 100)
    if ocr_rate < 80:
        recs.append("Améliorer les conditions d'éclairage sur le quai pour augmenter le taux OCR.")
    if ocr_rate < 95:
        recs.append("Vérifier manuellement les conteneurs avec OCR échoué avant validation.")
    if data.get("avg_processing_time", 0) > 3:
        recs.append("Optimiser la résolution des images pour accélérer le traitement.")
    if not recs:
        recs.append("Les opérations se sont déroulées normalement. Aucune action corrective requise.")
    recs.append("Archiver les images et ce rapport dans le système de gestion documentaire.")
    return recs


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_data = {
        "ship_name":    "MSC Rosaria",
        "dock_name":    "Quai 3",
        "sts_operator": "Ahmed Benali",
        "total":        42,
        "unloaded":     38,
        "ocr_errors":   4,
        "ocr_success_rate": 90.5,
        "avg_confidence":   88.2,
        "avg_processing_time": 1.23,
        "containers": [
            {"container_id": "MSCU1234567", "confidence_score": 0.92, "status": "déchargé", "date_detection": "2024-01-15 09:30"},
            {"container_id": None,          "confidence_score": 0.45, "status": "erreur OCR", "date_detection": "2024-01-15 09:31"},
        ],
    }
    pdf_bytes = generate_pdf(sample_data, output_path="test_report.pdf",
                              llm_summary="Résumé de test généré automatiquement.")
    print(f"✅  PDF généré ({len(pdf_bytes)} bytes) → test_report.pdf")
