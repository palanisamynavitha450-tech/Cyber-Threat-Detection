"""
AI Threat Detection page — interactive single prediction, real test sample loader,
batch analysis, and automatic alert logging.
"""
import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SELECTED_FEATURES, PROCESSED_DIR, LABEL_COLUMN
from src.threat_detection import ThreatDetector
from utils import generate_alert
from dashboard.theme import page_header, metric_card_html, severity_badge, plotly_dark_layout


@st.cache_resource
def _load_detector():
    det = ThreatDetector()
    det.load_models()
    return det


def _log_alert(prediction: str, confidence: float, features: dict):
    alert = generate_alert(prediction=prediction, confidence=confidence, features=features)
    alert["status"] = "Active"
    if "security_alerts" not in st.session_state:
        st.session_state["security_alerts"] = []
    st.session_state["security_alerts"].insert(0, alert)
    st.session_state["security_alerts"] = st.session_state["security_alerts"][:200]


def render():
    page_header("AI Threat Detection", "Analyze IoT network traffic and detect cyber threats", "🔍")

    try:
        detector = _load_detector()
    except Exception as e:
        st.error(f"⚠️ Models could not be loaded: {e}. Please train models first.")
        return

    tab1, tab2 = st.tabs(["🎯 Single Traffic Prediction", "📋 Batch Dataset Analysis"])

    with tab1:
        st.markdown("### Network Traffic Feature Input")
        st.caption(
            "Enter raw feature values manually, or load a real sample from the CICIoT2023 test split "
            "(note: test_processed.parquet stores standardized z-score values)."
        )

        # Option to load a real sample from test dataset
        test_path = os.path.join(PROCESSED_DIR, "test_processed.parquet")
        use_scaled_input = st.session_state.get("td_input_is_scaled", False)

        lc1, lc2, lc3 = st.columns([2, 1, 1])
        with lc1:
            sample_type = st.selectbox(
                "Quick-load a real test sample (optional)",
                ["Manual Input (Raw Values)", "Random Benign Sample (Scaled)", "Random Attack Sample (Scaled)"],
                key="td_sample_mode",
            )
        with lc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📥 Load Sample", use_container_width=True, key="td_load_sample_btn"):
                if sample_type == "Manual Input (Raw Values)":
                    for feat in SELECTED_FEATURES:
                        st.session_state[f"feat_{feat}"] = 0.0
                    st.session_state["td_input_is_scaled"] = False
                    st.session_state["td_true_label"] = None
                elif os.path.exists(test_path):
                    tdf = pd.read_parquet(test_path)
                    if "Benign" in sample_type:
                        sub = tdf[tdf[LABEL_COLUMN] == "BenignTraffic"]
                    else:
                        sub = tdf[tdf[LABEL_COLUMN] != "BenignTraffic"]
                    row = sub.sample(n=1).iloc[0]
                    for feat in SELECTED_FEATURES:
                        st.session_state[f"feat_{feat}"] = float(row[feat])
                    st.session_state["td_input_is_scaled"] = True
                    st.session_state["td_true_label"] = str(row[LABEL_COLUMN])
                st.rerun()
        with lc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Reset Zeros", use_container_width=True, key="td_reset_btn"):
                for feat in SELECTED_FEATURES:
                    st.session_state[f"feat_{feat}"] = 0.0
                st.session_state["td_input_is_scaled"] = False
                st.session_state["td_true_label"] = None
                st.rerun()

        if st.session_state.get("td_true_label"):
            st.info(f"Loaded real test sample — Ground Truth Label: **{st.session_state['td_true_label']}** (standardized z-scores)")
            use_scaled_input = True

        feature_values = {}
        cols = st.columns(4)
        for i, feat in enumerate(SELECTED_FEATURES):
            with cols[i % 4]:
                feature_values[feat] = st.number_input(
                    feat,
                    value=float(st.session_state.get(f"feat_{feat}", 0.0)),
                    format="%.4f",
                    key=f"feat_{feat}",
                )

        col_model, col_btn = st.columns([1, 1])
        with col_model:
            model_choice = st.selectbox("Detection Model", ["Random Forest", "XGBoost"], key="pred_model")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            predict_btn = st.button("🔍 Analyze Traffic", use_container_width=True)

        if predict_btn:
            model_key = "rf" if model_choice == "Random Forest" else "xgb"
            with st.spinner("Running AI threat classification..."):
                result = detector.predict_single(
                    feature_values, model_name=model_key, already_scaled=use_scaled_input
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📊 Detection Results")

            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.markdown(metric_card_html("Prediction", result["prediction"], "🎯", color="#22d3ee"), unsafe_allow_html=True)
            with r2:
                st.markdown(metric_card_html("Category", result["category"], "📁", color="#a78bfa"), unsafe_allow_html=True)
            with r3:
                sev = result["severity"]
                color_map = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b", "None": "#22c55e"}
                st.markdown(metric_card_html("Severity", sev, "⚠️", color=color_map.get(sev, "#22d3ee")), unsafe_allow_html=True)
            with r4:
                st.markdown(metric_card_html("Confidence", f"{result['confidence']:.2%}", "📈", color="#22c55e"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            ac1, ac2 = st.columns(2)
            anomaly_color = "#ef4444" if result["is_anomaly"] else "#22c55e"
            with ac1:
                anomaly_text = "ANOMALY DETECTED" if result["is_anomaly"] else "Normal Pattern"
                st.markdown(metric_card_html("Anomaly Status", anomaly_text, "🔔", color=anomaly_color), unsafe_allow_html=True)
            with ac2:
                st.markdown(metric_card_html("Anomaly Score", f"{result['anomaly_score']:.4f}", "📉", color="#14b8a6"), unsafe_allow_html=True)

            if result.get("probabilities"):
                st.markdown("### 📊 Top Class Probabilities")
                sorted_probs = sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True)[:10]
                fig = px.bar(
                    x=[v for _, v in sorted_probs],
                    y=[k for k, _ in sorted_probs],
                    orientation="h",
                    labels={"x": "Probability", "y": "Class"},
                    color=[v for _, v in sorted_probs],
                    color_continuous_scale="Tealgrn",
                )
                fig.update_layout(**plotly_dark_layout(height=340, yaxis={"autorange": "reversed"}))
                st.plotly_chart(fig, use_container_width=True)

            if result["category"] != "Benign":
                _log_alert(
                    result["prediction"],
                    result["confidence"],
                    {f: float(feature_values[f]) for f in SELECTED_FEATURES[:5]},
                )
                st.markdown(f"""
                <div class="cyber-card" style="border-color: {anomaly_color};">
                    <div style="color: {anomaly_color}; font-size: 1.15rem; font-weight: 700;">
                        🚨 SECURITY ALERT LOGGED
                    </div>
                    <p style="margin-top: 8px; margin-bottom: 0;">
                        Detected <strong>{result['prediction']}</strong>
                        (Category: {result['category']}, Severity: {severity_badge(result['severity'])}).
                        Confidence: <strong>{result['confidence']:.2%}</strong>. Added to Security Alerts Center.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### Batch Traffic Analysis (CICIoT2023 Test Split)")
        n_samples = st.slider("Number of test samples", 10, 500, 100, key="batch_n")
        model_choice_batch = st.selectbox("Model", ["Random Forest", "XGBoost"], key="batch_model")

        if st.button("🚀 Run Batch Analysis", use_container_width=True):
            model_key = "rf" if model_choice_batch == "Random Forest" else "xgb"
            with st.spinner("Analyzing batch..."):
                if not os.path.exists(test_path):
                    st.error("Test data not found.")
                    return
                test_df = pd.read_parquet(test_path).sample(n=min(n_samples, 500), random_state=42)
                results_df = detector.predict_batch(test_df, model_name=model_key, already_scaled=True)

            # Log top threats from batch into session alerts
            malicious_rows = results_df[results_df["predicted_category"] != "Benign"]
            for _, row in malicious_rows.head(15).iterrows():
                _log_alert(
                    row["predicted_label"],
                    float(row["confidence"]),
                    {f: float(row[f]) for f in SELECTED_FEATURES[:5]},
                )

            st.markdown("#### Detection Summary")
            sc1, sc2 = st.columns(2)
            with sc1:
                cat_counts = results_df["predicted_category"].value_counts()
                fig = px.pie(names=cat_counts.index, values=cat_counts.values, hole=0.42)
                fig.update_layout(**plotly_dark_layout(height=350, title="Predicted Categories"))
                st.plotly_chart(fig, use_container_width=True)
            with sc2:
                sev_counts = results_df["severity"].value_counts()
                fig2 = px.bar(
                    x=sev_counts.index, y=sev_counts.values,
                    color=sev_counts.index,
                    color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b", "None": "#22c55e"},
                )
                fig2.update_layout(**plotly_dark_layout(height=350, title="Severity Distribution"))
                st.plotly_chart(fig2, use_container_width=True)

            anomaly_count = int(results_df["is_anomaly"].sum())
            st.markdown(f"**Anomalies detected:** {anomaly_count} / {len(results_df)} ({anomaly_count / len(results_df):.1%})")

            display_cols = ["predicted_label", "predicted_category", "severity", "confidence", "anomaly_score", "is_anomaly"]
            if LABEL_COLUMN in results_df.columns:
                display_cols = [LABEL_COLUMN] + display_cols
            st.dataframe(results_df[display_cols].head(200), use_container_width=True, height=400)
