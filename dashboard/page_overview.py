"""
Home / Dashboard Overview page — landing page with system status, dataset overview,
model status, threat monitoring overview, quick navigation, and report export.
"""
import os
import sys
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, ARTIFACTS_DIR, MODELS_DIR, CATEGORY_SEVERITY
from utils import load_json, generate_csv_report, generate_pdf_report
from dashboard.theme import page_header, metric_card_html, status_pill, plotly_dark_layout


def _navigate_to(page_name: str):
    st.session_state["current_page"] = page_name
    st.rerun()


def render():
    page_header(
        "Home / Dashboard Overview",
        "Welcome to the AI-Based Cyber Threat Detection System for IoT Security",
        "🏠",
    )

    dist = load_json(os.path.join(PROCESSED_DIR, "class_distribution.json"))
    comparison = load_json(os.path.join(ARTIFACTS_DIR, "model_comparison.json"))
    fl_results = load_json(os.path.join(ARTIFACTS_DIR, "fl_results.json"))
    iso_info = load_json(os.path.join(ARTIFACTS_DIR, "iso_forest_info.json"))

    rf_ok = os.path.exists(os.path.join(MODELS_DIR, "random_forest.joblib"))
    xgb_ok = os.path.exists(os.path.join(MODELS_DIR, "xgboost_model.joblib"))
    iso_ok = os.path.exists(os.path.join(MODELS_DIR, "isolation_forest.joblib"))
    fl_ok = os.path.exists(os.path.join(MODELS_DIR, "federated_global_model.joblib"))

    # ── Welcome & System Status Hero Card ────────────────────
    st.markdown(f"""
    <div class="cyber-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div style="flex: 2; min-width: 260px;">
                <div class="cyber-card-header">🛡️ WELCOME • PRIVACY-PRESERVING IoT CYBERSECURITY</div>
                <h3 style="margin-top:4px; margin-bottom:8px;">AI-Based Cyber Threat Detection System</h3>
                <p style="margin-bottom:0; line-height:1.65; color:#cbd5e1;">
                    An intelligent IoT security platform powered by <strong>Random Forest</strong>,
                    <strong>XGBoost</strong>, <strong>Isolation Forest</strong> anomaly detection,
                    and <strong>Federated Learning (FedAvg)</strong> trained on the <strong>CICIoT2023</strong> dataset.
                </p>
            </div>
            <div style="flex: 1; min-width: 220px;">
                <div class="cyber-card-header">⚡ SYSTEM & MODEL STATUS</div>
                <div style="display:flex; flex-direction:column; gap:6px; margin-top:6px;">
                    <div>{status_pill("Random Forest: Loaded" if rf_ok else "Random Forest: Missing", rf_ok)}</div>
                    <div>{status_pill("XGBoost: Loaded" if xgb_ok else "XGBoost: Missing", xgb_ok)}</div>
                    <div>{status_pill("Isolation Forest: Loaded" if iso_ok else "Isolation Forest: Missing", iso_ok)}</div>
                    <div>{status_pill("Federated Model: Ready" if fl_ok else "Federated Model: Not Trained", fl_ok)}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Navigation ─────────────────────────────────────
    st.markdown("### ⚡ Quick Navigation")
    qn1, qn2, qn3, qn4, qn5 = st.columns(5)
    with qn1:
        if st.button("🔍 AI Threat Detection", use_container_width=True, key="qn_detect"):
            _navigate_to("🔍 AI Threat Detection")
    with qn2:
        if st.button("🔔 Anomaly Detection", use_container_width=True, key="qn_anom"):
            _navigate_to("🔔 Anomaly Detection")
    with qn3:
        if st.button("🚨 Security Alerts", use_container_width=True, key="qn_alerts"):
            _navigate_to("🚨 Security Alerts")
    with qn4:
        if st.button("📡 Traffic Replay", use_container_width=True, key="qn_replay"):
            _navigate_to("📡 Traffic Replay")
    with qn5:
        if st.button("🧠 Explainable AI", use_container_width=True, key="qn_xai"):
            _navigate_to("🧠 Explainable AI")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dataset Overview KPIs ────────────────────────────────
    total_samples = sum(dist.get("label_distribution", {}).values()) if dist else 0
    num_attacks = max(0, len(dist.get("label_distribution", {})) - 1) if dist else 0
    benign_count = dist.get("label_distribution", {}).get("BenignTraffic", 0)
    attack_count = total_samples - benign_count

    st.markdown("### 📊 Dataset Overview (Processed CICIoT2023)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card_html("Total Samples", f"{total_samples:,}", "📊", color="#22d3ee"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card_html("Attack Classes", str(num_attacks), "⚠️", color="#f97316"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card_html("Benign Traffic", f"{benign_count:,}", "✅", color="#22c55e"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card_html("Malicious Traffic", f"{attack_count:,}", "🚨", color="#ef4444"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Model Status & Performance Summary ───────────────────
    if comparison:
        st.markdown("### 🤖 Model Status & Evaluation")
        cols = st.columns(len(comparison))
        for i, (model_name, metrics) in enumerate(comparison.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div class="cyber-card-header">{model_name}</div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 10px;">
                        <div><span style="color: #94a3b8; font-size: 0.78rem;">Accuracy</span><br>
                            <span style="color: #22c55e; font-size: 1.25rem; font-weight: 700;">{metrics['accuracy']:.2%}</span></div>
                        <div><span style="color: #94a3b8; font-size: 0.78rem;">Precision</span><br>
                            <span style="color: #22d3ee; font-size: 1.25rem; font-weight: 700;">{metrics['precision']:.2%}</span></div>
                        <div><span style="color: #94a3b8; font-size: 0.78rem;">Recall</span><br>
                            <span style="color: #14b8a6; font-size: 1.25rem; font-weight: 700;">{metrics['recall']:.2%}</span></div>
                        <div><span style="color: #94a3b8; font-size: 0.78rem;">F1 Score</span><br>
                            <span style="color: #a78bfa; font-size: 1.25rem; font-weight: 700;">{metrics['f1_score']:.2%}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Threat Monitoring Overview Charts ────────────────────
    col_left, col_right = st.columns(2)

    if dist and "category_distribution" in dist:
        cat_dist = dist["category_distribution"]
        with col_left:
            st.markdown("### 🎯 Attack Category Distribution")
            fig = px.pie(
                names=list(cat_dist.keys()),
                values=list(cat_dist.values()),
                hole=0.45,
            )
            fig.update_layout(**plotly_dark_layout(showlegend=True, height=400))
            fig.update_traces(
                textinfo="percent+label",
                marker=dict(line=dict(color="#050a18", width=2)),
            )
            st.plotly_chart(fig, use_container_width=True)

    if dist and "label_distribution" in dist:
        label_dist = dist["label_distribution"]
        with col_right:
            st.markdown("### 📊 Top 15 Attack Labels")
            sorted_labels = sorted(label_dist.items(), key=lambda x: x[1], reverse=True)[:15]
            fig = px.bar(
                x=[v for _, v in sorted_labels],
                y=[k for k, _ in sorted_labels],
                orientation="h",
                labels={"x": "Sample Count", "y": "Attack Label"},
                color=[v for _, v in sorted_labels],
                color_continuous_scale="Tealgrn",
            )
            fig.update_layout(**plotly_dark_layout(height=400, yaxis={"autorange": "reversed"}))
            st.plotly_chart(fig, use_container_width=True)

    # ── Severity Breakdown ───────────────────────────────────
    if dist and "category_distribution" in dist:
        st.markdown("### 🔒 Threat Severity Breakdown")
        severity_counts = {}
        for cat, count in dist["category_distribution"].items():
            sev = CATEGORY_SEVERITY.get(cat, "Unknown")
            severity_counts[sev] = severity_counts.get(sev, 0) + count

        cols = st.columns(len(severity_counts))
        colors = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b", "None": "#22c55e"}
        icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "None": "🟢"}
        for i, (sev, cnt) in enumerate(sorted(severity_counts.items())):
            with cols[i]:
                st.markdown(
                    metric_card_html(sev, f"{cnt:,}", icons.get(sev, "🔵"), color=colors.get(sev, "#22d3ee")),
                    unsafe_allow_html=True,
                )

    # ── Federated Learning Summary ───────────────────────────
    if fl_results:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🌐 Federated Learning Status")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(metric_card_html("FL Clients", str(fl_results.get("num_clients", 0)), "🖥️"), unsafe_allow_html=True)
        with fc2:
            st.markdown(metric_card_html("FL Rounds", str(fl_results.get("num_rounds", 0)), "🔄", color="#a78bfa"), unsafe_allow_html=True)
        with fc3:
            st.markdown(
                metric_card_html("Global Accuracy", f"{fl_results.get('final_global_accuracy', 0):.2%}", "🎯", color="#22c55e"),
                unsafe_allow_html=True,
            )

    # ── Security Report Export ───────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 Export Security Analysis Report")
    exp1, exp2 = st.columns(2)
    alerts = st.session_state.get("security_alerts", [])
    with exp1:
        csv_bytes = generate_csv_report(dist, comparison, fl_results, alerts)
        st.download_button(
            "📄 Download CSV Report",
            data=csv_bytes,
            file_name="cyber_threat_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp2:
        pdf_bytes = generate_pdf_report(dist, comparison, fl_results, iso_info, alerts)
        st.download_button(
            "📑 Download PDF Report",
            data=pdf_bytes,
            file_name="cyber_threat_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
