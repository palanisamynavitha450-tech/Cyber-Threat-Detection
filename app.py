"""
AI-Based Cyber Threat Detection System — Main Streamlit Application
Unified global layout, single sidebar navigation, and consistent theme.
"""
import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import (
    STREAMLIT_PAGE_TITLE, STREAMLIT_PAGE_ICON, STREAMLIT_LAYOUT,
    MODELS_DIR, PROCESSED_DIR,
)
from dashboard.theme import inject_custom_css, render_top_banner

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ─── Global Navigation Items ─────────────────────────────────────────────────
NAV_ITEMS = [
    "🏠 Home / Dashboard Overview",
    "📂 Dataset Analysis",
    "📊 Model Performance",
    "🔍 AI Threat Detection",
    "🔔 Anomaly Detection",
    "🌐 Federated Learning",
    "🚨 Security Alerts",
    "📡 Traffic Replay",
    "🧠 Explainable AI",
    "🩺 System Health",
    "ℹ️ About Project",
]

# ─── Session State Initialization ────────────────────────────────────────────
if "current_page" not in st.session_state or st.session_state["current_page"] not in NAV_ITEMS:
    st.session_state["current_page"] = NAV_ITEMS[0]

if "security_alerts" not in st.session_state:
    st.session_state["security_alerts"] = []

if "last_traffic_results" not in st.session_state:
    st.session_state["last_traffic_results"] = None


def _check_core_assets():
    models_ok = all(
        os.path.exists(os.path.join(MODELS_DIR, f))
        for f in ["random_forest.joblib", "xgboost_model.joblib", "isolation_forest.joblib"]
    )
    data_ok = all(
        os.path.exists(os.path.join(PROCESSED_DIR, f))
        for f in ["train_processed.parquet", "test_processed.parquet", "label_encoder.joblib", "scaler.joblib"]
    )
    return models_ok, data_ok


models_ready, data_ready = _check_core_assets()

# ─── Common Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 14px 0 10px 0;">
        <div style="font-size: 2.6rem; line-height: 1;">🛡️</div>
        <div style="font-family: 'Poppins', sans-serif; font-size: 1.25rem; font-weight: 700;
            margin-top: 8px; background: linear-gradient(135deg, #22d3ee, #14b8a6, #a78bfa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            AI Cyber Threat Detection
        </div>
        <p style="color: #94a3b8; font-size: 0.74rem; margin-top: 2px; margin-bottom: 0;">
            Federated Learning & Anomaly AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    selected_page = st.radio(
        "Navigation",
        NAV_ITEMS,
        index=NAV_ITEMS.index(st.session_state["current_page"]),
        label_visibility="collapsed",
        key="sidebar_nav_radio",
    )
    if selected_page != st.session_state["current_page"]:
        st.session_state["current_page"] = selected_page
        st.rerun()

    st.markdown("---")
    alert_cnt = len(st.session_state.get("security_alerts", []))
    st.markdown(f"""
    <div style="background: rgba(15,23,42,0.75); border: 1px solid rgba(6,182,212,0.2);
                border-radius: 10px; padding: 10px 12px; font-size: 0.75rem;">
        <div style="color: #22d3ee; font-weight: 600; margin-bottom: 4px;">SYSTEM SUMMARY</div>
        <div>Models: <strong style="color:{'#4ade80' if models_ready else '#fb923c'};">{'Ready' if models_ready else 'Missing'}</strong></div>
        <div>Dataset: <strong style="color:{'#4ade80' if data_ready else '#fb923c'};">{'Ready' if data_ready else 'Missing'}</strong></div>
        <div>Session Alerts: <strong style="color:#f87171;">{alert_cnt}</strong></div>
    </div>
    """, unsafe_allow_html=True)

# ─── Unified Top Header ──────────────────────────────────────────────────────
active = st.session_state["current_page"]
render_top_banner(active, models_ready, data_ready)

# ─── Page Router ─────────────────────────────────────────────────────────────
if active == "🏠 Home / Dashboard Overview":
    from dashboard.page_overview import render
    render()
elif active == "📂 Dataset Analysis":
    from dashboard.page_dataset import render
    render()
elif active == "📊 Model Performance":
    from dashboard.page_model_performance import render
    render()
elif active == "🔍 AI Threat Detection":
    from dashboard.page_threat_detection import render
    render()
elif active == "🔔 Anomaly Detection":
    from dashboard.page_anomaly import render
    render()
elif active == "🌐 Federated Learning":
    from dashboard.page_federated import render
    render()
elif active == "🚨 Security Alerts":
    from dashboard.page_alerts import render
    render()
elif active == "📡 Traffic Replay":
    from dashboard.page_traffic import render
    render()
elif active == "🧠 Explainable AI":
    from dashboard.page_explainable_ai import render
    render()
elif active == "🩺 System Health":
    from dashboard.page_system_health import render
    render()
elif active == "ℹ️ About Project":
    from dashboard.page_about import render
    render()
