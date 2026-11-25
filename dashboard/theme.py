"""
Unified CSS theme and reusable UI components for the AI-Based Cyber Threat Detection System.
Dark navy blue background with cyan, teal, and violet accents.
"""
import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700&display=swap');

    /* ── Global App Background ─────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #050a18 0%, #0a1128 45%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }

    h1, h2, h3, h4 {
        font-family: 'Poppins', 'Inter', sans-serif !important;
        color: #f1f5f9 !important;
        letter-spacing: -0.01em;
    }

    p, li, label, span {
        color: #cbd5e1;
    }

    /* ── Sidebar ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #040814 0%, #081026 100%) !important;
        border-right: 1px solid rgba(6, 182, 212, 0.22);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(6, 182, 212, 0.12);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 5px;
        transition: all 0.2s ease;
        width: 100%;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(6, 182, 212, 0.12);
        border-color: rgba(6, 182, 212, 0.45);
    }

    /* ── Top Global Banner ─────────────────────────────────── */
    .global-banner {
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.12) 0%, rgba(139, 92, 246, 0.12) 50%, rgba(20, 184, 166, 0.10) 100%);
        border: 1px solid rgba(6, 182, 212, 0.28);
        border-radius: 14px;
        padding: 14px 22px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        box-shadow: 0 4px 24px rgba(6, 182, 212, 0.08);
    }
    .global-banner-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #22d3ee, #14b8a6, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Metric Cards ──────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(6, 182, 212, 0.07) 100%);
        border: 1px solid rgba(6, 182, 212, 0.22);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: all 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(34, 211, 238, 0.5);
        transform: translateY(-2px);
    }
    div[data-testid="stMetric"] label {
        color: #22d3ee !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 1.65rem !important;
    }

    /* ── Tabs ──────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(6, 182, 212, 0.16);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        font-weight: 600;
    }

    /* ── Buttons ───────────────────────────────────────────── */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.25);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(139, 92, 246, 0.4);
    }

    /* ── Inputs & Selectboxes ──────────────────────────────── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(6, 182, 212, 0.25) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }

    /* ── Custom Cyber Card ─────────────────────────────────── */
    .cyber-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(17, 24, 39, 0.78) 100%);
        border: 1px solid rgba(6, 182, 212, 0.22);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.28);
    }
    .cyber-card-header {
        color: #22d3ee;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }

    /* ── Severity & Status Badges ──────────────────────────── */
    .severity-critical {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .severity-high {
        background: rgba(249, 115, 22, 0.2);
        border: 1px solid #f97316;
        color: #fdba74;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .severity-medium {
        background: rgba(245, 158, 11, 0.2);
        border: 1px solid #f59e0b;
        color: #fcd34d;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .severity-none {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid #22c55e;
        color: #86efac;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-pill-ok {
        background: rgba(34, 197, 94, 0.16);
        border: 1px solid rgba(34, 197, 94, 0.5);
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-pill-warn {
        background: rgba(249, 115, 22, 0.16);
        border: 1px solid rgba(249, 115, 22, 0.5);
        color: #fb923c;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }

    /* ── Glow Title ────────────────────────────────────────── */
    .glow-title {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #22d3ee 0%, #14b8a6 45%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1.25;
    }

    /* Hide default footer/menu */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #050a18; }
    ::-webkit-scrollbar-thumb { background: #06b6d4; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def render_top_banner(active_page: str, models_ready: bool, data_ready: bool):
    """Consistent global header rendered across every page."""
    sys_badge = (
        '<span class="status-pill-ok">● SYSTEM ONLINE</span>'
        if (models_ready and data_ready)
        else '<span class="status-pill-warn">● PARTIAL ASSETS</span>'
    )
    st.markdown(f"""
    <div class="global-banner">
        <div>
            <div class="global-banner-title">🛡️ AI-Based Cyber Threat Detection System</div>
            <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
                Privacy-Preserving IoT Security • Federated Learning & Anomaly Detection • Active Module: <strong style="color:#22d3ee;">{active_page}</strong>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            {sys_badge}
        </div>
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header."""
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 2rem; line-height: 1;">{icon}</span>
            <span class="glow-title">{title}</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px; margin-bottom: 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card_html(label: str, value, icon: str = "", delta: str = "",
                     color: str = "#22d3ee"):
    """Return HTML for a styled metric card."""
    delta_html = ""
    if delta:
        delta_html = f'<div style="color: #22c55e; font-size: 0.8rem; margin-top: 4px;">▲ {delta}</div>'
    return f"""
    <div class="cyber-card" style="text-align: center; padding: 18px 14px;">
        <div style="font-size: 1.7rem; margin-bottom: 6px;">{icon}</div>
        <div class="cyber-card-header" style="margin-bottom: 4px;">{label}</div>
        <div style="color: {color}; font-size: 1.65rem; font-weight: 700; word-break: break-word;">{value}</div>
        {delta_html}
    </div>
    """


def severity_badge(severity: str) -> str:
    s = severity.lower()
    css_class = f"severity-{s}" if s in ["critical", "high", "medium", "none"] else "severity-medium"
    return f'<span class="{css_class}">{severity}</span>'


def status_pill(label: str, ok: bool = True) -> str:
    cls = "status-pill-ok" if ok else "status-pill-warn"
    return f'<span class="{cls}">{label}</span>'


def plotly_dark_layout(**overrides) -> dict:
    """
    Return a dark theme layout dict for Plotly charts, safely merging
    any xaxis/yaxis/legend overrides so duplicate keyword arguments never occur.
    """
    base = {
        "paper_bgcolor": "rgba(10, 17, 40, 0)",
        "plot_bgcolor": "rgba(15, 23, 42, 0.55)",
        "font": {"color": "#cbd5e1", "family": "Inter, sans-serif"},
        "xaxis": {"gridcolor": "rgba(6,182,212,0.12)", "zerolinecolor": "rgba(6,182,212,0.12)"},
        "yaxis": {"gridcolor": "rgba(6,182,212,0.12)", "zerolinecolor": "rgba(6,182,212,0.12)"},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
        "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
        "colorway": [
            "#06b6d4", "#8b5cf6", "#14b8a6", "#22d3ee",
            "#a78bfa", "#34d399", "#f97316", "#ef4444",
        ],
    }
    for k, v in overrides.items():
        if k in ("xaxis", "yaxis", "legend", "margin", "font") and isinstance(v, dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base
