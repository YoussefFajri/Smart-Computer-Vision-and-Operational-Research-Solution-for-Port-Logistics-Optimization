"""
Marsa Maroc — Port Logistics AI Dashboard
Streamlit multi-page administrative interface.
4 pages: Overview · History · Images · Report
"""
from __future__ import annotations

import io
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

API_BASE = os.getenv("API_BASE_URL", "http://localhost:5000")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Port Logistics AI — Marsa Maroc",
    page_icon=Path("container_ai_project/.static/marsamaroc.png"),
    layout="wide",
    
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Force Dark Mode Theme */
    .stApp {
        background-color: #0c101d !important;
        background-image: none !important;
        color: #e2e8f0 !important;
    }

    /* Header styling */
    header, [data-testid="stHeader"] {
        background-color: rgba(12, 16, 29, 0.9) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #090e1a !important;
        background-image: none !important;
        box-shadow: 2px 0 15px rgba(0,0,0,0.5) !important;
        border-right: 1px solid #1a2235 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Hide default radio labels & style the items */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 8px !important;
        padding-top: 10px !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important;
        color: #8a9bb4 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        margin-bottom: 2px !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: #161e30 !important;
        color: #ffffff !important;
        transform: translateX(4px);
    }

    /* Highlight the selected option */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background-color: #0f5cf2 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(15, 92, 242, 0.4) !important;
    }

    /* Remove standard streamlit radio dots */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stRadioButton"] {
        display: none !important;
    }

    /* Custom Dashboard Card Container */
    .dashboard-card {
        background-color: #121824 !important;
        border: 1px solid #1c2436 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    .card-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 15px !important;
        border-bottom: 1px solid #1c2436 !important;
        padding-bottom: 10px !important;
    }

    .card-title {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .card-subtitle {
        font-size: 0.8rem !important;
        color: #718096 !important;
    }

    /* KPI styling */
    .kpi-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 15px !important;
        padding-bottom: 12px !important;
        border-bottom: 1px solid rgba(28, 36, 54, 0.5) !important;
    }
    .kpi-row:last-child {
        border-bottom: none !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    .kpi-label {
        font-size: 0.85rem !important;
        color: #a0aec0 !important;
        font-weight: 500 !important;
    }

    .kpi-value-large {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    .kpi-trend-positive {
        font-size: 0.8rem !important;
        color: #00e676 !important;
        font-weight: 600 !important;
        margin-left: 6px !important;
    }
    
    .kpi-trend-negative {
        font-size: 0.8rem !important;
        color: #ff1744 !important;
        font-weight: 600 !important;
        margin-left: 6px !important;
    }

    /* Input fields dark overrides */
    .stTextInput input, .stSelectbox > div > div, .stFileUploader > div {
        background-color: #121824 !important;
        border: 1px solid #1c2436 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus, .stSelectbox > div > div:focus-within {
        border-color: #0B2B5E;
        box-shadow: 0 0 0 2px rgba(11,43,94,0.2);
    }

    /* Hide default streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Helper for Page Headers ───────────────────────────────────────────────────
def render_page_header(title: str, subtitle: str, icon_filename: str):
    icon_path = PROJECT_ROOT / "static" / icon_filename
    col1, col2 = st.columns([1, 15])
    with col1:
        if icon_path.exists():
            st.image(str(icon_path), use_container_width=True)
        else:
            st.markdown("🔹")
    with col2:
        st.markdown(f"<h2 style='margin-top: -15px; color: #0B2B5E; font-weight: 800;'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b; font-size: 1.1rem; margin-top: -15px; margin-bottom: 20px;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0; margin-bottom: 30px; border-color: #e2e8f0;'>", unsafe_allow_html=True)



# ── API Helpers ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_stats() -> dict:
    try:
        r = requests.get(f"{API_BASE}/stats", timeout=5)
        return r.json()
    except Exception:
        return {}


@st.cache_data(ttl=5)
def fetch_containers(limit: int = 300) -> list[dict]:
    try:
        r = requests.get(f"{API_BASE}/containers", params={"limit": limit}, timeout=5)
        return r.json().get("containers", [])
    except Exception:
        return []


def check_api() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=5)
def fetch_decharge(limit: int = 50) -> list[dict]:
    try:
        r = requests.get(f"{API_BASE}/containers/decharge", params={"limit": limit}, timeout=5)
        return r.json().get("containers", [])
    except Exception:
        return []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 15px 0 25px 0; display: flex; align-items: center; gap: 10px;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#0f5cf2"/>
            <path d="M2 17L12 22L22 17" stroke="#0f5cf2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="#0f5cf2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span style="font-size: 1.3rem; font-weight: 800; color: #ffffff; letter-spacing: 1px;">MARSA AI</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "Computer Vision", "Terminal Ops", "Analytics", "Reporting", "Settings"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API status
    api_ok = check_api()
    status_color = "#00e676" if api_ok else "#ff1744"
    status_text  = "Connecté" if api_ok else "Hors ligne"
    st.markdown(
        f"<div style='text-align:center; padding: 5px 0;'>"
        f"<span style='color:{status_color}; font-size:0.85rem; font-weight:600;'>● API Flask — {status_text}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; font-size:0.7rem; opacity:0.5; color:#8a9bb4;'>"
        f"v1.0 — {datetime.now().strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD (Vue Générale)
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    # Custom dashboard top bar header to match the reference image
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
        <div>
            <h1 style="margin: 0; color: #ffffff; font-size: 1.7rem; font-weight: 700;">Port Logistics AI | Overview</h1>
            <p style="margin: 3px 0 0 0; color: #718096; font-size: 0.9rem;">
                Real-time status &nbsp;&nbsp;<span style="color: #00e676; font-weight: 600;">● Camera: CV_14_YARD</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    stats = fetch_stats()

    if not stats:
        if not api_ok:
            st.warning("⚠️ L'API Flask n'est pas démarrée. Lancez `python backend/app.py` d'abord.")
        else:
            st.info("Aucune donnée enregistrée. Commencez par détecter des conteneurs dans la page Images.")
    else:
        # Create columns: Left (CCTV and Logs), Right (Yard, KPIs, Charts)
        col_left, col_right = st.columns([1, 1.4])

        with col_left:
            # ── 1. Real-Time Terminal CCTV ──
            st.markdown('<div class="dashboard-card"><div class="card-header"><span class="card-title">Real-Time Terminal CCTV</span><span style="color:#00d2ff; font-size:1.1rem;">●</span></div>', unsafe_allow_html=True)
            
            # Fetch last container for image
            containers = fetch_containers(5)
            last_img_path = None
            last_container_id = "MSCU1234567"
            last_status = "Détecté"
            last_dock = "Quai 3"
            last_type = "MSC"
            last_size = "40ft"
            
            if containers and len(containers) > 0:
                recent_c = containers[0]
                last_container_id = recent_c.get("container_id") or "MSCU1234567"
                last_status = recent_c.get("status") or "Détecté"
                last_dock = recent_c.get("dock_name") or "Quai 3"
                if recent_c.get("annotated_path") and Path(recent_c["annotated_path"]).exists():
                    last_img_path = recent_c["annotated_path"]
                elif recent_c.get("image_path") and Path(recent_c["image_path"]).exists():
                    last_img_path = recent_c["image_path"]

                # Extract container details if possible
                if last_container_id.startswith("MSC"):
                    last_type = "MSC"
                elif last_container_id.startswith("CMA"):
                    last_type = "CMA CGM"
                elif last_container_id.startswith("TGH"):
                    last_type = "Textainer"
                else:
                    last_type = "Standard"
                
                # Mock size based on length
                last_size = "40ft" if len(last_container_id) > 10 else "20ft"

            # Fallback to an existing static image if no last image is found
            if not last_img_path:
                static_files = list(Path(PROJECT_ROOT / "static").glob("annotated_*.jpg"))
                if static_files:
                    last_img_path = str(static_files[0])
                else:
                    last_img_path = None
            
            if last_img_path:
                st.image(last_img_path, use_container_width=True)
            else:
                st.markdown("<div style='height: 250px; background-color: #1a2333; display: flex; align-items: center; justify-content: center; border-radius: 8px; color: #a0aec0;'>Aucun flux vidéo disponible</div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: rgba(18, 24, 36, 0.85); padding: 12px; border-radius: 8px; border: 1px solid #1c2436; margin-top: 10px;">
                <div style="font-size: 0.8rem; font-weight: 600; color: #ff1744; text-transform: uppercase;">Container Detected</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-top: 4px; letter-spacing: 0.5px;">[ {last_container_id} 98% ]</div>
                <div style="font-size: 0.85rem; color: #a0aec0; margin-top: 4px;">Type: {last_type} &nbsp;|&nbsp; Size: {last_size}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 2. Activity Log ──
            st.markdown('<div class="dashboard-card"><div class="card-header"><span class="card-title">Activity Log</span><span style="color:#718096; font-size:0.85rem;">...</span></div>', unsafe_allow_html=True)
            if containers and len(containers) > 0:
                for c in containers[:4]:
                    dt_str = "10:14 AM"
                    if c.get("date_detection"):
                        try:
                            dt = datetime.fromisoformat(c["date_detection"])
                            dt_str = dt.strftime("%H:%M %p")
                        except Exception:
                            pass
                    cid = c.get("container_id") or "Illisible"
                    dock = c.get("dock_name") or "CV_14_YARD"
                    st.markdown(f"<div style='font-size: 0.85rem; margin-bottom: 10px; color: #a0aec0;'><span style='color: #718096; font-weight:600;'>{dt_str}</span> - <strong>{cid}</strong> Detected - {dock}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size: 0.85rem; color: #718096;'>Aucun log d'activité</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════════════
        # SECTION DÉCHARGÉ — Full width below the two columns
        # ══════════════════════════════════════════════════════════════════
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <span class="card-title">📦 Conteneurs Déchargés</span>
            <span style="color:#00e676; font-size:0.85rem; font-weight:600;">Auto-détectés par OCR</span>
        </div>
        """, unsafe_allow_html=True)

        decharge_list = fetch_decharge(20)
        if decharge_list:
            # Build a styled HTML table
            table_html = '<div style="overflow-x: auto;">' \
                '<table style="width:100%; border-collapse: collapse; font-size: 0.85rem;">' \
                '<thead>' \
                '<tr style="border-bottom: 2px solid #1c2436; text-align: left;">' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">ID Conteneur</th>' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">Date &amp; Heure</th>' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">Quai</th>' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">Navire</th>' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">Confiance OCR</th>' \
                '<th style="padding: 10px 12px; color: #718096; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">Statut</th>' \
                '</tr>' \
                '</thead>' \
                '<tbody>'
            for c in decharge_list:
                cid = c.get("container_id", "—")
                dt_str = "—"
                if c.get("date_detection"):
                    try:
                        dt = datetime.fromisoformat(c["date_detection"])
                        dt_str = dt.strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        dt_str = c["date_detection"][:16]
                dock = c.get("dock_name", "—")
                ship = c.get("ship_name", "—")
                conf = c.get("ocr_confidence", 0)
                conf_pct = f"{float(conf) * 100:.0f}%" if conf else "—"
                conf_color = "#00e676" if conf and float(conf) >= 0.8 else "#ffab00" if conf and float(conf) >= 0.5 else "#ff1744"

                table_html += (
                    f'<tr style="border-bottom: 1px solid rgba(28, 36, 54, 0.5); transition: background 0.2s;">'
                    f'<td style="padding: 10px 12px;">'
                    f'<span style="color: #00d2ff; font-weight: 700; font-family: \'Courier New\', monospace; font-size: 0.9rem; letter-spacing: 0.5px;">{cid}</span>'
                    f'</td>'
                    f'<td style="padding: 10px 12px; color: #a0aec0;">{dt_str}</td>'
                    f'<td style="padding: 10px 12px; color: #a0aec0;">{dock}</td>'
                    f'<td style="padding: 10px 12px; color: #a0aec0;">{ship}</td>'
                    f'<td style="padding: 10px 12px;">'
                    f'<span style="color: {conf_color}; font-weight: 600;">{conf_pct}</span>'
                    f'</td>'
                    f'<td style="padding: 10px 12px;">'
                    f'<span style="background-color: rgba(0, 230, 118, 0.15); color: #00e676; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">✅ Déchargé</span>'
                    f'</td>'
                    f'</tr>'
                )
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.8rem; color: #718096;">{len(decharge_list)} conteneur(s) déchargé(s) affichés</span>
                <span style="font-size: 0.8rem; color: #00e676; font-weight: 600;">Total déchargés : {stats.get('unloaded', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px 0; color: #718096;">
                <div style="font-size: 2rem; margin-bottom: 8px;">📦</div>
                <div style="font-size: 0.9rem;">Aucun conteneur déchargé pour l'instant</div>
                <div style="font-size: 0.8rem; color: #4a5568; margin-top: 4px;">Les conteneurs avec un ID valide détecté par OCR apparaîtront ici automatiquement</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            # ── 3. Operational Status & 3D Yard ──
            st.markdown('<div class="dashboard-card"><div class="card-header"><span class="card-title">Operational Status</span><span style="color:#00e676; font-size:0.85rem; font-weight:600;">Terminal: Active</span></div>', unsafe_allow_html=True)
            
            c_yard, c_metrics = st.columns([1.6, 1])
            
            with c_yard:
                st.components.v1.iframe(f"{API_BASE}/yard/view?minimal=true", height=280, scrolling=False)
                st.markdown("""
                <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.8rem; color: #a0aec0; text-transform: uppercase;">Yard Capacity:</span>
                    <span style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">78%</span>
                </div>
                """, unsafe_allow_html=True)
            
            with c_metrics:
                st.markdown(f"""
                <div class="kpi-row">
                    <div>
                        <div class="kpi-label">Total Containers</div>
                        <div class="kpi-value-large">{stats.get("total", 0)}<span class="kpi-trend-positive">+8.2%</span></div>
                    </div>
                </div>
                <div class="kpi-row">
                    <div>
                        <div class="kpi-label">Gate Throughput</div>
                        <div class="kpi-value-large">310<span style="font-size:0.75rem; color:#a0aec0; font-weight:normal;"> TEU/hr</span><span class="kpi-trend-positive">+3.1%</span></div>
                    </div>
                </div>
                <div class="kpi-row">
                    <div>
                        <div class="kpi-label">Vessel TAT</div>
                        <div class="kpi-value-large">14.5<span style="font-size:0.75rem; color:#a0aec0; font-weight:normal;"> hrs</span><span class="kpi-trend-negative">-0.8%</span></div>
                    </div>
                </div>
                <div class="kpi-row">
                    <div>
                        <div class="kpi-label">CV Efficiency</div>
                        <div class="kpi-value-large">{stats.get("ocr_success_rate", 0.0):.1f}%<span class="kpi-trend-positive">98.4%</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            # ── 4. Performance Metrics (Charts) ──
            st.markdown('<div class="dashboard-card"><div class="card-header"><span class="card-title">Performance Metrics</span></div>', unsafe_allow_html=True)
            c_chart1, c_chart2 = st.columns(2)
            
            with c_chart1:
                st.markdown("<div style='font-size: 0.85rem; color: #a0aec0; margin-bottom: 5px; font-weight:600;'>Container Flow (TEU/hr) <span style='color:#00d2ff; float:right;'>310 TEU/hr</span></div>", unsafe_allow_html=True)
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    y=[150, 180, 240, 210, 190, 280, 350, 290, 250, 220, 280, 310],
                    mode='lines',
                    line=dict(color='#00d2ff', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 210, 255, 0.1)',
                    name='Flow'
                ))
                fig1.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=5, b=5, l=5, r=5),
                    height=130,
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    showlegend=False
                )
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
                st.markdown("<div style='font-size: 0.7rem; color: #718096; display: flex; justify-content: space-between;'><span>last 12 hrs</span><span>current</span></div>", unsafe_allow_html=True)

            with c_chart2:
                st.markdown("<div style='font-size: 0.85rem; color: #a0aec0; margin-bottom: 5px; font-weight:600;'>Object Detection Accuracy (%) <span style='color:#00e676; float:right;'>97.2%</span></div>", unsafe_allow_html=True)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    y=[95.1, 95.8, 96.2, 95.9, 96.5, 97.1, 96.8, 97.4, 97.9, 98.2, 97.8, 98.4],
                    mode='lines',
                    line=dict(color='#00e676', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 230, 118, 0.1)',
                    name='Accuracy'
                ))
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=5, b=5, l=5, r=5),
                    height=130,
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                st.markdown("<div style='font-size: 0.7rem; color: #718096; display: flex; justify-content: space-between;'><span>last 12 hrs</span><span>average</span></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Analytics":
    render_page_header(
        "Historique des Opérations",
        "Consultez et filtrez l'historique complet des détections",
        "historique_icon.png"
    )

    containers = fetch_containers(500)
    if not containers:
        st.info("Aucun conteneur enregistré pour l'instant.")
    else:
        df = pd.DataFrame(containers)

        # ── Filters ───────────────────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "Statut",
                ["Tous"] + sorted(df["status"].dropna().unique().tolist()),
            )
        with col2:
            dock_filter = st.selectbox(
                "Quai",
                ["Tous"] + sorted(df["dock_name"].dropna().unique().tolist()),
            )
        with col3:
            search = st.text_input("🔍 Rechercher un ID conteneur")

        # Apply filters
        filtered = df.copy()
        if status_filter != "Tous":
            filtered = filtered[filtered["status"] == status_filter]
        if dock_filter != "Tous":
            filtered = filtered[filtered["dock_name"] == dock_filter]
        if search:
            filtered = filtered[
                filtered["container_id"].fillna("").str.contains(search.upper(), na=False)
            ]

        st.markdown(f"`{len(filtered)}` enregistrement(s) trouvé(s)")

        # ── Display table ──────────────────────────────────────────────────────
        display_cols = ["id", "container_id", "date_detection", "dock_name",
                        "ship_name", "sts_operator", "status", "confidence_score"]
        available = [c for c in display_cols if c in filtered.columns]
        display_df = filtered[available].copy()
        display_df.columns = [c.replace("_", " ").title() for c in available]

        if "Confidence Score" in display_df.columns:
            display_df["Confidence Score"] = display_df["Confidence Score"].apply(
                lambda x: f"{float(x)*100:.1f}%" if pd.notna(x) else "—"
            )

        st.dataframe(display_df, use_container_width=True, height=500)

        # ── Export CSV ────────────────────────────────────────────────────────
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exporter CSV",
            data=csv,
            file_name=f"historique_conteneurs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — UPLOAD MANIFEST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Terminal Ops":
    render_page_header(
        "Upload du Manifeste Navire",
        "Importez la liste prévisionnelle des conteneurs pour anticiper le plan de cour.",
        "upload_icon.png"
    )

    st.markdown('<div class="section-header">Fichier CSV</div>', unsafe_allow_html=True)
    st.info("Le fichier doit contenir les colonnes `container_id`, `size`, `weight`, et `departure_time`.")
    uploaded_manifest = st.file_uploader(
        "Sélectionnez le fichier manifeste (CSV)",
        type=["csv"],
        label_visibility="collapsed"
    )

    if uploaded_manifest:
        try:
            df_manifest = pd.read_csv(uploaded_manifest)
            st.dataframe(df_manifest.head(5), use_container_width=True)
            
            if st.button("📤 Envoyer le Manifeste", type="primary", use_container_width=True):
                if not api_ok:
                    st.error("❌ L'API Flask n'est pas disponible.")
                else:
                    with st.spinner("Traitement du manifeste et planification de cour..."):
                        uploaded_manifest.seek(0)
                        try:
                            resp = requests.post(
                                f"{API_BASE}/manifest/upload",
                                files={"file": (uploaded_manifest.name, uploaded_manifest.read(), "text/csv")},
                                timeout=30
                            )
                            if resp.status_code == 200:
                                result = resp.json()
                                msg = result.get("message", "Manifeste chargé avec succès !")
                                st.markdown(f'<div class="success-banner">✅ {msg}</div>', unsafe_allow_html=True)
                            else:
                                try:
                                    err = resp.json().get("error", "Erreur inconnue")
                                except:
                                    err = resp.text
                                st.markdown(f'<div class="error-banner">❌ Erreur: {err}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'envoi: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur de lecture du fichier CSV: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — IMAGES DÉTECTÉES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Computer Vision":
    render_page_header(
        "Détection & Analyse d'Images",
        "Analysez les images de conteneurs via YOLOv8 et EasyOCR",
        "image_icon.webp"
    )

    # ── Session info form ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Informations de la session</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        ship_name = st.text_input("Nom du navire", placeholder="Ex: MSC Rosaria")
    with col2:
        dock_name = st.text_input("Quai", placeholder="Ex: Quai 3")
    with col3:
        sts_operator = st.text_input("Responsable STS", placeholder="Ex: Ahmed Benali")

    # ── Upload ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Charger une image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Glisser-déposer ou cliquer pour sélectionner",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded:
        col_orig, col_annot = st.columns(2)
        with col_orig:
            st.markdown("**Image originale**")
            st.image(uploaded, use_container_width=True)

        if not api_ok:
            st.error("❌ L'API Flask n'est pas disponible. Lancez `python backend/app.py`.")
        else:
            if st.button("🔍 Lancer la Détection", type="primary", use_container_width=True):
                uploaded.seek(0)
                with st.spinner("Analyse en cours… YOLO + OCR"):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/detect",
                            files={"file": (uploaded.name, uploaded.read(), uploaded.type)},
                            data={
                                "ship_name":    ship_name,
                                "dock_name":    dock_name,
                                "sts_operator": sts_operator,
                            },
                            timeout=120,
                        )
                        result = resp.json()

                        if resp.status_code == 200 and result.get("success"):
                            # Show annotated image
                            ann_path = result.get("annotated_image", "")
                            if ann_path and Path(ann_path).exists():
                                with col_annot:
                                    st.markdown("**Image annotée**")
                                    st.image(ann_path, use_container_width=True)

                            # Summary banner
                            n = result.get("total_detected", 0)
                            t = result.get("processing_time", 0)
                            st.markdown(
                                f'<div class="success-banner">✅ {n} conteneur(s) détecté(s) en {t:.2f}s</div>',
                                unsafe_allow_html=True,
                            )

                            # OCR results table
                            containers_out = result.get("containers", [])
                            if containers_out:
                                st.markdown('<div class="section-header">Résultats OCR</div>', unsafe_allow_html=True)
                                rows = []
                                for i, c in enumerate(containers_out, 1):
                                    rows.append({
                                        "#":              i,
                                        "ID Conteneur":   c.get("container_id") or "❌ Illisible",
                                        "Texte OCR brut": c.get("raw_text", ""),
                                        "Conf. YOLO":     f"{c.get('yolo_confidence', 0)*100:.0f}%",
                                        "Conf. OCR":      f"{c.get('ocr_confidence', 0)*100:.0f}%",
                                        "Valide":         "✅" if c.get("is_valid") else "⚠️",
                                    })
                                st.dataframe(pd.DataFrame(rows), use_container_width=True)

                            # Invalidate cache
                            fetch_stats.clear()
                            fetch_containers.clear()
                        else:
                            st.markdown(
                                f'<div class="error-banner">❌ Erreur: {result.get("error", "Inconnue")}</div>',
                                unsafe_allow_html=True,
                            )
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout — le traitement prend trop de temps.")
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — RAPPORT PDF
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Reporting":
    render_page_header(
        "Génération du Rapport PDF",
        "Générez un rapport de synthèse détaillé des opérations",
        "rapport_icon.png"
    )

    stats = fetch_stats()

    # ── Preview stats ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Aperçu des données à inclure</div>', unsafe_allow_html=True)
    if stats:
        c1, c2, c3 = st.columns(3)
        c1.metric("Conteneurs détectés", stats.get("total", 0))
        c2.metric("Déchargés",           stats.get("unloaded", 0))
        c3.metric("Erreurs OCR",         stats.get("ocr_errors", 0))
    else:
        st.info("Aucune donnée disponible.")

    st.markdown('<div class="section-header">Informations optionnelles</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        ship_r = st.text_input("Navire", key="rpt_ship", placeholder="MSC Rosaria")
    with col2:
        dock_r = st.text_input("Quai", key="rpt_dock", placeholder="Quai 3")
    with col3:
        oper_r = st.text_input("Responsable STS", key="rpt_oper", placeholder="Ahmed Benali")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Generate button ────────────────────────────────────────────────────────
    if st.button("📥 Générer et Télécharger le Rapport PDF", type="primary", use_container_width=True):
        if not api_ok:
            st.error("❌ L'API Flask n'est pas disponible.")
        else:
            with st.spinner("Génération du rapport en cours…"):
                try:
                    params = {}
                    if ship_r: params["ship_name"]    = ship_r
                    if dock_r: params["dock_name"]    = dock_r
                    if oper_r: params["sts_operator"] = oper_r

                    resp = requests.get(f"{API_BASE}/report/pdf", params=params, timeout=30)
                    if resp.status_code == 200:
                        fname = f"rapport_marsa_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                        st.download_button(
                            label="📄 Cliquez ici pour télécharger le PDF",
                            data=resp.content,
                            file_name=fname,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.markdown(
                            '<div class="success-banner">✅ Rapport généré avec succès !</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ Erreur API: {resp.text[:200]}")
                except Exception as e:
                    st.error(f"❌ {e}")

    # ── Info ───────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Contenu du rapport PDF"):
        st.markdown("""
        Le rapport PDF généré contient :
        - **Page de couverture** avec la date et l'identité de session
        - **Tableau des statistiques** (total, déchargements, taux OCR)
        - **Liste complète des conteneurs** (jusqu'à 60 entrées)
        - **Section anomalies** (identifiants illisibles)
        - **Résumé IA** généré automatiquement
        - **Recommandations opérationnelles**
        """)


elif page == "Settings":
    render_page_header(
        "Paramètres du Système",
        "Configurez les paramètres généraux de l'API et de détection",
        "upload_icon.png"
    )
    
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><span class="card-title">Seuils de Détection & OCR</span></div>', unsafe_allow_html=True)
    
    conf = st.slider("Seuil de confiance YOLOv8", min_value=0.1, max_value=1.0, value=0.45, step=0.05)
    ocr_lang = st.selectbox("Langues de lecture EasyOCR", ["en", "fr", "ar", "en,fr"])
    
    st.markdown(f"Configuration actuelle : YOLOv8 `conf={conf}` | EasyOCR `lang={ocr_lang}`")
    if st.button("Sauvegarder les Paramètres", type="primary", use_container_width=True):
        st.success("Paramètres enregistrés (simulation).")
    
    st.markdown('</div>', unsafe_allow_html=True)
