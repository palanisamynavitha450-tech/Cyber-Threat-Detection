"""
Traffic Replay page — simulated dataset-based IoT traffic replay using CICIoT2023 test split.
Clearly distinguished from live NIC packet capture.
"""
import os
import sys
import time
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, SELECTED_FEATURES, LABEL_COLUMN
from src.threat_detection import ThreatDetector
from utils import generate_alert
from dashboard.theme import page_header, metric_card_html, severity_badge, plotly_dark_layout


@st.cache_resource
def _get_detector():
    det = ThreatDetector()
    det.load_models()
    return det


def render():
    page_header("Traffic Replay", "Dataset-based IoT traffic replay & threat detection", "📡")

    st.info(
        "ℹ️ **Simulated Dataset Replay Mode:** Flows are sampled from the actual `CICIoT2023` "
        "`test_processed.parquet` split and evaluated by the trained ML & Anomaly models in real time "
        "(not live network interface packet capture)."
    )

    try:
        detector = _get_detector()
    except Exception as e:
        st.error(f"⚠️ Models not loaded: {e}")
        return

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        n_packets = st.slider("Traffic flows to replay", 20, 300, 100, key="traffic_n")
    with col_ctrl2:
        model_choice = st.selectbox("Detection Model", ["Random Forest", "XGBoost"], key="traffic_model")
    with col_ctrl3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Start Traffic Replay", use_container_width=True)

    if run_btn:
        model_key = "rf" if model_choice == "Random Forest" else "xgb"
        with st.spinner("Replaying CICIoT2023 traffic flows..."):
            test_path = os.path.join(PROCESSED_DIR, "test_processed.parquet")
            if not os.path.exists(test_path):
                st.error("Test data not found.")
                return

            test_df = pd.read_parquet(test_path)
            sample = test_df.sample(n=min(n_packets, len(test_df)), random_state=int(time.time()) % 10000)
            results = detector.predict_batch(sample, model_name=model_key, already_scaled=True)
            st.session_state["last_traffic_results"] = results

            # Log generated alerts to session state
            malicious_traffic = results[results["predicted_category"] != "Benign"]
            new_alerts = []
            for _, row in malicious_traffic.head(25).iterrows():
                alert = generate_alert(
                    prediction=row["predicted_label"],
                    confidence=float(row["confidence"]),
                    features={f: float(row[f]) for f in SELECTED_FEATURES[:3]},
                )
                alert["status"] = "Active"
                new_alerts.append(alert)
            if new_alerts:
                existing = st.session_state.get("security_alerts", [])
                st.session_state["security_alerts"] = (new_alerts + existing)[:200]

    results = st.session_state.get("last_traffic_results", None)
    if results is None:
        st.caption("Click **Start Traffic Replay** above to replay CICIoT2023 flows and inspect predictions.")
        return

    # ── Traffic Summary ──────────────────────────────────────
    st.markdown("### 📊 Replayed Traffic Summary")
    total = len(results)
    benign = int((results["predicted_category"] == "Benign").sum())
    malicious = total - benign
    anomalies = int(results["is_anomaly"].sum())

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(metric_card_html("Total Flows", f"{total:,}", "📡", color="#22d3ee"), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card_html("Benign", f"{benign:,}", "✅", color="#22c55e"), unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card_html("Malicious", f"{malicious:,}", "🚨", color="#ef4444"), unsafe_allow_html=True)
    with m4:
        st.markdown(metric_card_html("Anomalies", f"{anomalies:,}", "🔔", color="#f97316"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visualizations ───────────────────────────────────────
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Traffic by Predicted Category")
        cat_counts = results["predicted_category"].value_counts()
        fig = px.pie(names=cat_counts.index, values=cat_counts.values, hole=0.42)
        fig.update_layout(**plotly_dark_layout(height=360))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Traffic Rate vs Total Packet Size (Scaled)")
        if "Rate" in results.columns and "Tot size" in results.columns:
            fig2 = px.scatter(
                results, x="Rate", y="Tot size",
                color="predicted_category",
                hover_data=["predicted_label", "confidence"],
                opacity=0.75,
            )
            fig2.update_layout(**plotly_dark_layout(height=360, title="Flow Rate vs Packet Size"))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Alerts Preview ───────────────────────────────────────
    st.markdown("### 🚨 Alerts Generated from Replay")
    malicious_rows = results[results["predicted_category"] != "Benign"]
    if len(malicious_rows) == 0:
        st.success("✅ No threats detected in this replayed batch.")
    else:
        for _, row in malicious_rows.head(10).iterrows():
            sev = row["severity"]
            sev_color = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b"}.get(sev, "#22d3ee")
            st.markdown(f"""
            <div class="cyber-card" style="border-left: 4px solid {sev_color}; padding: 10px 16px; margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="color:{sev_color};">{row['predicted_label']}</strong>
                        <span style="margin-left:10px;">{severity_badge(sev)}</span>
                    </div>
                    <span style="color:#22d3ee; font-size:0.82rem;">Confidence: {row['confidence']:.2%}</span>
                </div>
                <div style="color:#94a3b8; font-size:0.8rem; margin-top:4px;">
                    Category: {row['predicted_category']} | Anomaly Score: {row['anomaly_score']:.4f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Replay Table & Export ────────────────────────────────
    st.markdown("### 📋 Replayed Flow Details")
    display_cols = [LABEL_COLUMN, "predicted_label", "predicted_category", "severity", "confidence", "anomaly_score", "is_anomaly"]
    display_cols = [c for c in display_cols if c in results.columns]
    st.dataframe(results[display_cols].head(200), use_container_width=True, height=380)

    csv_data = results[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📄 Download Replay Results (CSV)",
        data=csv_data,
        file_name="traffic_replay_results.csv",
        mime="text/csv",
    )
