"""
Live Security Alert Center — displays real detected threats from model predictions,
severity, confidence scores, timestamps, interactive alert status, and report export.
"""
import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, ARTIFACTS_DIR
from src.threat_detection import ThreatDetector
from utils import load_json, generate_csv_report, generate_pdf_report
from dashboard.theme import page_header, metric_card_html, severity_badge, plotly_dark_layout


@st.cache_resource
def _get_detector():
    det = ThreatDetector()
    det.load_models()
    return det


def render():
    page_header("Security Alerts", "Live Security Alert Center for detected IoT cyber threats", "🚨")

    alerts = st.session_state.get("security_alerts", [])

    # Controls to scan real test traffic or clear alerts
    c_act1, c_act2, c_act3 = st.columns([2, 1, 1])
    with c_act1:
        model_choice = st.selectbox("Scan Model", ["Random Forest", "XGBoost"], key="alert_scan_model")
    with c_act2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Scan 100 Test Flows", use_container_width=True, key="alert_scan_btn"):
            det = _get_detector()
            mkey = "rf" if model_choice == "Random Forest" else "xgb"
            _, new_alerts = det.replay_traffic(n_samples=100, model_name=mkey)
            st.session_state["security_alerts"] = (new_alerts + alerts)[:200]
            st.rerun()
    with c_act3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Alerts", use_container_width=True, key="alert_clear_btn"):
            st.session_state["security_alerts"] = []
            st.rerun()

    alerts = st.session_state.get("security_alerts", [])

    # ── KPIs ─────────────────────────────────────────────────
    total_alerts = len(alerts)
    crit_cnt = sum(1 for a in alerts if a.get("severity") == "Critical")
    high_cnt = sum(1 for a in alerts if a.get("severity") == "High")
    active_cnt = sum(1 for a in alerts if a.get("status", "Active") == "Active")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(metric_card_html("Total Alerts", str(total_alerts), "🚨", color="#22d3ee"), unsafe_allow_html=True)
    with k2:
        st.markdown(metric_card_html("Critical", str(crit_cnt), "🔴", color="#ef4444"), unsafe_allow_html=True)
    with k3:
        st.markdown(metric_card_html("High Severity", str(high_cnt), "🟠", color="#f97316"), unsafe_allow_html=True)
    with k4:
        st.markdown(metric_card_html("Active Alerts", str(active_cnt), "⚡", color="#a78bfa"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not alerts:
        st.info(
            "No security alerts recorded in this session yet. Click **Scan 100 Test Flows** above "
            "or run detection on the **AI Threat Detection** / **Traffic Replay** pages."
        )
        return

    # ── Filters ──────────────────────────────────────────────
    f1, f2, f3 = st.columns(3)
    with f1:
        sev_filter = st.multiselect(
            "Filter by Severity",
            ["Critical", "High", "Medium"],
            default=["Critical", "High", "Medium"],
            key="alert_sev_filter",
        )
    with f2:
        cats = sorted({a.get("category", "Unknown") for a in alerts})
        cat_filter = st.multiselect("Filter by Category", cats, default=cats, key="alert_cat_filter")
    with f3:
        stat_filter = st.multiselect(
            "Filter by Status",
            ["Active", "Investigating", "Resolved"],
            default=["Active", "Investigating", "Resolved"],
            key="alert_stat_filter",
        )

    filtered = [
        a for a in alerts
        if a.get("severity") in sev_filter
        and a.get("category") in cat_filter
        and a.get("status", "Active") in stat_filter
    ]

    # ── Alert Breakdown Chart ────────────────────────────────
    if filtered:
        adf = pd.DataFrame(filtered)
        c_left, c_right = st.columns(2)
        with c_left:
            fig1 = px.pie(adf, names="category", hole=0.42, title="Alerts by Attack Category")
            fig1.update_layout(**plotly_dark_layout(height=320))
            st.plotly_chart(fig1, use_container_width=True)
        with c_right:
            sev_counts = adf["severity"].value_counts()
            fig2 = px.bar(
                x=sev_counts.index, y=sev_counts.values,
                color=sev_counts.index,
                color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b"},
                title="Alerts by Severity",
            )
            fig2.update_layout(**plotly_dark_layout(height=320))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Alert Feed & Status Management ───────────────────────
    st.markdown(f"### 📋 Alert Feed ({len(filtered)} matching)")
    for idx, alert in enumerate(filtered[:30]):
        sev = alert.get("severity", "Medium")
        sev_color = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b"}.get(sev, "#22d3ee")
        status = alert.get("status", "Active")

        col_card, col_stat = st.columns([4, 1])
        with col_card:
            st.markdown(f"""
            <div class="cyber-card" style="border-left: 4px solid {sev_color}; padding: 12px 16px; margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div>
                        <strong style="color:{sev_color};">{alert.get('alert_id', 'ALERT')}</strong>
                        <span style="margin-left:10px;">{severity_badge(sev)}</span>
                        <span style="margin-left:10px; color:#22d3ee; font-size:0.8rem;">Status: {status}</span>
                    </div>
                    <span style="color:#94a3b8; font-size:0.78rem;">{alert.get('timestamp', '')}</span>
                </div>
                <div style="margin-top:6px; color:#e2e8f0; font-size:0.9rem;">
                    Attack: <strong>{alert.get('prediction')}</strong> | Category: <strong>{alert.get('category')}</strong> | Confidence: <strong>{alert.get('confidence', 0):.2%}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_stat:
            new_status = st.selectbox(
                "Status",
                ["Active", "Investigating", "Resolved"],
                index=["Active", "Investigating", "Resolved"].index(status),
                key=f"alert_stat_{idx}_{alert.get('alert_id', idx)}",
                label_visibility="collapsed",
            )
            if new_status != status:
                alert["status"] = new_status

    # ── Export Alerts ────────────────────────────────────────
    st.markdown("### 📥 Export Alert Report")
    dist = load_json(os.path.join(PROCESSED_DIR, "class_distribution.json"))
    comparison = load_json(os.path.join(ARTIFACTS_DIR, "model_comparison.json"))
    fl_results = load_json(os.path.join(ARTIFACTS_DIR, "fl_results.json"))
    iso_info = load_json(os.path.join(ARTIFACTS_DIR, "iso_forest_info.json"))

    e1, e2 = st.columns(2)
    with e1:
        st.download_button(
            "📄 Download Alerts CSV",
            data=generate_csv_report(dist, comparison, fl_results, filtered),
            file_name="security_alerts_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with e2:
        st.download_button(
            "📑 Download Alerts PDF",
            data=generate_pdf_report(dist, comparison, fl_results, iso_info, filtered),
            file_name="security_alerts_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
