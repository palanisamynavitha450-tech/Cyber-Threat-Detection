"""
Anomaly Detection page — Isolation Forest analysis and anomaly visualization.
"""
import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, MODELS_DIR, ARTIFACTS_DIR, SELECTED_FEATURES, LABEL_COLUMN
from utils import load_json
from dashboard.theme import page_header, metric_card_html, plotly_dark_layout


@st.cache_data(ttl=300)
def _load_anomaly_data(n=3000):
    test_path = os.path.join(PROCESSED_DIR, "test_processed.parquet")
    if not os.path.exists(test_path):
        return None
    df = pd.read_parquet(test_path)
    if len(df) > n:
        df = df.sample(n=n, random_state=42)
    return df


def render():
    page_header("Anomaly Detection", "Isolation Forest unsupervised anomaly scoring and monitoring", "🔔")

    iso_info_path = os.path.join(ARTIFACTS_DIR, "iso_forest_info.json")
    iso_info = load_json(iso_info_path) if os.path.exists(iso_info_path) else {}

    df = _load_anomaly_data()
    if df is None:
        st.warning("⚠️ Processed test data not found. Run preprocessing first.")
        return

    iso_path = os.path.join(MODELS_DIR, "isolation_forest.joblib")
    if not os.path.exists(iso_path):
        st.warning("⚠️ Isolation Forest model not found. Train models first.")
        return

    iso_model = joblib.load(iso_path)

    X = df[SELECTED_FEATURES].values
    scores = iso_model.score_samples(X)
    predictions = iso_model.predict(X)
    df = df.copy()
    df["anomaly_score"] = scores
    df["is_anomaly"] = predictions == -1
    df["anomaly_label"] = df["is_anomaly"].map({True: "Anomaly", False: "Normal"})

    # ── KPIs ─────────────────────────────────────────────────
    total = len(df)
    anomalies = int(df["is_anomaly"].sum())
    normal = total - anomalies
    rate = (anomalies / total * 100) if total > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Total Analyzed", f"{total:,}", "📊", color="#22d3ee"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Anomalies", f"{anomalies:,}", "🚨", color="#ef4444"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card_html("Normal", f"{normal:,}", "✅", color="#22c55e"), unsafe_allow_html=True)
    with c4:
        st.markdown(
            metric_card_html("Anomaly Rate", f"{rate:.1f}%", "📈", color="#ef4444" if rate > 20 else "#f97316"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Score Distribution", "🗺️ Anomaly Map", "📋 Detailed View"])

    with tab1:
        st.markdown("### Anomaly Score Distribution")
        fig = px.histogram(
            df, x="anomaly_score", color="anomaly_label",
            nbins=60, barmode="overlay",
            color_discrete_map={"Anomaly": "#ef4444", "Normal": "#06b6d4"},
        )
        fig.update_layout(**plotly_dark_layout(height=400, title="Isolation Forest Anomaly Score Distribution"))
        threshold = iso_info.get("threshold", None)
        if threshold is not None:
            fig.add_vline(
                x=threshold, line_dash="dash", line_color="#f97316",
                annotation_text=f"Threshold: {threshold:.4f}",
            )
        st.plotly_chart(fig, use_container_width=True)

        if "attack_category" in df.columns:
            st.markdown("### Average Anomaly Score by Attack Category")
            cat_scores = df.groupby("attack_category")["anomaly_score"].mean().sort_values()
            fig2 = px.bar(
                x=cat_scores.values, y=cat_scores.index, orientation="h",
                color=cat_scores.values, color_continuous_scale="RdYlGn",
                labels={"x": "Mean Anomaly Score", "y": "Attack Category"},
            )
            fig2.update_layout(**plotly_dark_layout(height=400))
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### Anomaly Feature Scatter Plot")
        feat_x = st.selectbox("X-axis feature", SELECTED_FEATURES, index=0, key="anom_x")
        feat_y = st.selectbox("Y-axis feature", SELECTED_FEATURES, index=1, key="anom_y")

        fig = px.scatter(
            df, x=feat_x, y=feat_y, color="anomaly_label",
            size=np.abs(df["anomaly_score"]),
            hover_data=[LABEL_COLUMN, "anomaly_score"],
            color_discrete_map={"Anomaly": "#ef4444", "Normal": "#06b6d4"},
            opacity=0.65,
        )
        fig.update_layout(**plotly_dark_layout(height=500, title=f"Anomalies: {feat_x} vs {feat_y}"))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### Anomaly Details")
        view_choice = st.radio("Filter", ["All", "Anomalies Only", "Normal Only"], horizontal=True, key="anom_filter")
        if view_choice == "Anomalies Only":
            view_df = df[df["is_anomaly"]]
        elif view_choice == "Normal Only":
            view_df = df[~df["is_anomaly"]]
        else:
            view_df = df

        display_cols = [LABEL_COLUMN, "attack_category", "anomaly_score", "anomaly_label"] + SELECTED_FEATURES[:5]
        display_cols = [c for c in display_cols if c in view_df.columns]
        st.dataframe(view_df[display_cols].head(300), use_container_width=True, height=400)
        st.caption(f"Showing {min(300, len(view_df)):,} of {len(view_df):,} rows")
