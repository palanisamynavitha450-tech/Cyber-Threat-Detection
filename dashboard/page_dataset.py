"""
Dataset Analysis page — browse, filter, and analyze the CICIoT2023 dataset.
"""
import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DIR, SELECTED_FEATURES, LABEL_COLUMN
from utils import load_json
from dashboard.theme import page_header, metric_card_html, plotly_dark_layout


@st.cache_data(ttl=600)
def _load_sample(n=5000):
    """Load a sample from processed training data for exploration."""
    path = os.path.join(PROCESSED_DIR, "train_processed.parquet")
    if os.path.exists(path):
        df = pd.read_parquet(path)
        if len(df) > n:
            df = df.sample(n=n, random_state=42)
        return df
    return None


def render():
    page_header("Dataset Analysis", "Explore the CICIoT2023 IoT network traffic dataset", "📂")

    dist = load_json(os.path.join(PROCESSED_DIR, "class_distribution.json"))
    df = _load_sample()

    if df is None:
        st.warning("⚠️ Processed data not found. Please run the preprocessing pipeline first.")
        return

    # ── Dataset Stats ────────────────────────────────────────
    total_processed = sum(dist.get("label_distribution", {}).values()) if dist else len(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Processed Rows", f"{total_processed:,}", "📊", color="#22d3ee"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Selected Features", str(len(SELECTED_FEATURES)), "🔢", color="#a78bfa"), unsafe_allow_html=True)
    with c3:
        num_labels = len(dist.get("label_distribution", {})) if dist else df[LABEL_COLUMN].nunique()
        st.markdown(metric_card_html("Traffic Classes", str(num_labels), "🏷️", color="#14b8a6"), unsafe_allow_html=True)
    with c4:
        missing = int(df[SELECTED_FEATURES].isna().sum().sum())
        st.markdown(
            metric_card_html("Missing Values", str(missing), "✅" if missing == 0 else "⚠️",
                             color="#22c55e" if missing == 0 else "#ef4444"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Data Preview", "📊 Feature Analysis", "🏷️ Class Distribution", "📈 Correlations"]
    )

    with tab1:
        st.markdown("#### Data Preview (5,000-row sample of scaled features)")
        labels = ["All"] + sorted(df[LABEL_COLUMN].unique().tolist())
        selected_label = st.selectbox("Filter by Label", labels, key="ds_filter_label")
        display_df = df if selected_label == "All" else df[df[LABEL_COLUMN] == selected_label]
        st.dataframe(display_df.head(200), use_container_width=True, height=400)
        st.caption(f"Showing {min(200, len(display_df)):,} of {len(display_df):,} sampled rows")

    with tab2:
        st.markdown("#### Feature Summary Statistics")
        stats = df[SELECTED_FEATURES].describe().T
        stats.columns = [c.capitalize() for c in stats.columns]
        st.dataframe(stats, use_container_width=True, height=380)

        st.markdown("#### Feature Distribution")
        selected_feat = st.selectbox("Select feature", SELECTED_FEATURES, key="ds_feat_dist")
        fig = px.histogram(df, x=selected_feat, nbins=50, color="attack_category" if "attack_category" in df.columns else LABEL_COLUMN)
        fig.update_layout(**plotly_dark_layout(height=430, title=f"Distribution of {selected_feat}"))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("#### Full Label Distribution")
        if dist and "label_distribution" in dist:
            label_data = dist["label_distribution"]
        else:
            label_data = df[LABEL_COLUMN].value_counts().to_dict()

        ld_df = pd.DataFrame(list(label_data.items()), columns=["Label", "Count"]).sort_values("Count", ascending=False)

        fig = px.bar(
            ld_df, x="Count", y="Label", orientation="h",
            color="Count", color_continuous_scale="Tealgrn",
        )
        fig.update_layout(
            **plotly_dark_layout(
                height=max(420, len(ld_df) * 24),
                yaxis={"autorange": "reversed"},
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        if dist and "category_distribution" in dist:
            st.markdown("#### Attack Category Distribution")
            cat_data = dist["category_distribution"]
            fig2 = px.pie(names=list(cat_data.keys()), values=list(cat_data.values()), hole=0.42)
            fig2.update_layout(**plotly_dark_layout(height=400))
            st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        st.markdown("#### Feature Correlation Heatmap (Top 15 Features)")
        top_features = SELECTED_FEATURES[:15]
        corr = df[top_features].corr()
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r")
        fig.update_layout(**plotly_dark_layout(height=520, title="Feature Correlations (Top 15)"))
        st.plotly_chart(fig, use_container_width=True)
