"""
Explainable AI (XAI) page — Global feature importance and per-sample prediction explanations.
"""
import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, ARTIFACTS_DIR, SELECTED_FEATURES, LABEL_COLUMN
from src.threat_detection import ThreatDetector
from utils import load_json
from dashboard.theme import page_header, metric_card_html, plotly_dark_layout


@st.cache_resource
def _get_detector():
    det = ThreatDetector()
    det.load_models()
    return det


def render():
    page_header("Explainable AI", "Understand model decisions with global & local feature attributions", "🧠")

    rf_results = load_json(os.path.join(ARTIFACTS_DIR, "rf_results.json"))
    xgb_results = load_json(os.path.join(ARTIFACTS_DIR, "xgb_results.json"))

    tab1, tab2 = st.tabs(["🌐 Global Feature Importance", "🔬 Local Sample Explanation"])

    with tab1:
        st.markdown("### Global Feature Importance (Random Forest vs XGBoost)")
        col1, col2 = st.columns(2)
        if rf_results and "feature_importances" in rf_results:
            with col1:
                imp_rf = pd.DataFrame(
                    list(rf_results["feature_importances"].items()),
                    columns=["Feature", "Importance"],
                ).sort_values("Importance", ascending=True).tail(15)
                fig1 = px.bar(
                    imp_rf, x="Importance", y="Feature", orientation="h",
                    color="Importance", color_continuous_scale="Tealgrn",
                    title="Random Forest — Top 15 Features",
                )
                fig1.update_layout(**plotly_dark_layout(height=460))
                st.plotly_chart(fig1, use_container_width=True)

        if xgb_results and "feature_importances" in xgb_results:
            with col2:
                imp_xgb = pd.DataFrame(
                    list(xgb_results["feature_importances"].items()),
                    columns=["Feature", "Importance"],
                ).sort_values("Importance", ascending=True).tail(15)
                fig2 = px.bar(
                    imp_xgb, x="Importance", y="Feature", orientation="h",
                    color="Importance", color_continuous_scale="Purp",
                    title="XGBoost — Top 15 Features",
                )
                fig2.update_layout(**plotly_dark_layout(height=460))
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### Explain Why a Traffic Sample Was Classified as Malicious or Benign")
        test_path = os.path.join(PROCESSED_DIR, "test_processed.parquet")
        if not os.path.exists(test_path):
            st.warning("⚠️ Processed test data not found.")
            return

        detector = _get_detector()
        tdf = pd.read_parquet(test_path)

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            target_labels = sorted(tdf[LABEL_COLUMN].unique().tolist())
            chosen_label = st.selectbox("Select Traffic Class to Sample", target_labels, key="xai_label")
        with c2:
            model_choice = st.selectbox("Model", ["Random Forest", "XGBoost"], key="xai_model")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            explain_btn = st.button("🧠 Explain Sample", use_container_width=True, key="xai_btn")

        if explain_btn or "xai_last_exp" in st.session_state:
            if explain_btn:
                sub = tdf[tdf[LABEL_COLUMN] == chosen_label]
                sample_row = sub.sample(n=1).iloc[0]
                feat_dict = {f: float(sample_row[f]) for f in SELECTED_FEATURES}
                mkey = "rf" if model_choice == "Random Forest" else "xgb"
                exp = detector.explain_prediction(feat_dict, model_name=mkey, already_scaled=True)
                exp["true_label"] = str(sample_row[LABEL_COLUMN])
                st.session_state["xai_last_exp"] = exp

            exp = st.session_state["xai_last_exp"]
            pr = exp["prediction_result"]

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(metric_card_html("True Label", exp["true_label"], "🏷️", color="#22d3ee"), unsafe_allow_html=True)
            with m2:
                st.markdown(metric_card_html("Predicted", pr["prediction"], "🎯", color="#a78bfa"), unsafe_allow_html=True)
            with m3:
                st.markdown(metric_card_html("Confidence", f"{pr['confidence']:.2%}", "📈", color="#22c55e"), unsafe_allow_html=True)
            with m4:
                anom_txt = "Anomaly" if pr["is_anomaly"] else "Normal"
                st.markdown(metric_card_html("Isolation Forest", anom_txt, "🔔", color="#ef4444" if pr["is_anomaly"] else "#22c55e"), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="cyber-card" style="margin-top:12px;">
                <div class="cyber-card-header">📝 AI Decision Explanation</div>
                <p style="margin-bottom:0; color:#e2e8f0; line-height:1.6;">{exp['summary']}</p>
            </div>
            """, unsafe_allow_html=True)

            cdf = pd.DataFrame(exp["contributions"][:12]).sort_values("local_impact", ascending=True)
            fig = px.bar(
                cdf, x="local_impact", y="feature", orientation="h",
                color="z_score", color_continuous_scale="RdBu_r",
                hover_data=["global_importance", "z_score"],
                title="Top 12 Contributing Features (Importance × |Z-Score Deviation|)",
                labels={"local_impact": "Local Attribution Impact", "feature": "Feature", "z_score": "Z-Score"},
            )
            fig.update_layout(**plotly_dark_layout(height=420))
            st.plotly_chart(fig, use_container_width=True)
