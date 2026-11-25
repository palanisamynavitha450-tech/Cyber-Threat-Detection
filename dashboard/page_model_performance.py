"""
Model Performance page — detailed evaluation metrics, confusion matrix, feature importance,
and PDF/CSV report export.
"""
import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ARTIFACTS_DIR, PROCESSED_DIR
from utils import load_json, generate_csv_report, generate_pdf_report
from dashboard.theme import page_header, metric_card_html, plotly_dark_layout


def render():
    page_header("Model Performance", "Comprehensive evaluation metrics and comparative analysis", "📊")

    rf_results = load_json(os.path.join(ARTIFACTS_DIR, "rf_results.json"))
    xgb_results = load_json(os.path.join(ARTIFACTS_DIR, "xgb_results.json"))
    comparison = load_json(os.path.join(ARTIFACTS_DIR, "model_comparison.json"))
    fl_results = load_json(os.path.join(ARTIFACTS_DIR, "fl_results.json"))
    iso_info = load_json(os.path.join(ARTIFACTS_DIR, "iso_forest_info.json"))
    dist = load_json(os.path.join(PROCESSED_DIR, "class_distribution.json"))

    if not rf_results and not xgb_results:
        st.warning("⚠️ Model results not found. Train models first.")
        return

    # ── Model Comparison ─────────────────────────────────────
    if comparison:
        st.markdown("### 🏆 Model Comparison")
        metrics_names = ["accuracy", "precision", "recall", "f1_score"]
        fig = go.Figure()
        for model_name, metrics in comparison.items():
            fig.add_trace(go.Bar(
                name=model_name,
                x=[m.replace("_", " ").title() for m in metrics_names],
                y=[metrics[m] for m in metrics_names],
                text=[f"{metrics[m]:.4f}" for m in metrics_names],
                textposition="outside",
            ))
        fig.update_layout(
            **plotly_dark_layout(
                barmode="group",
                height=400,
                title="Model Comparison — Key Evaluation Metrics",
                yaxis={"range": [0, 1.12]},
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Tabs for each model ──────────────────────────────────
    models = {}
    if rf_results:
        models["Random Forest"] = rf_results
    if xgb_results:
        models["XGBoost"] = xgb_results

    tabs = st.tabs([f"📊 {name}" for name in models.keys()])

    for tab, (model_name, results) in zip(tabs, models.items()):
        with tab:
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(metric_card_html("Accuracy", f"{results['accuracy']:.2%}", "🎯", color="#22c55e"), unsafe_allow_html=True)
            with k2:
                st.markdown(metric_card_html("Precision", f"{results['precision']:.2%}", "📌", color="#22d3ee"), unsafe_allow_html=True)
            with k3:
                st.markdown(metric_card_html("Recall", f"{results['recall']:.2%}", "🔍", color="#14b8a6"), unsafe_allow_html=True)
            with k4:
                st.markdown(metric_card_html("F1 Score", f"{results['f1_score']:.2%}", "📊", color="#a78bfa"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            sub1, sub2, sub3, sub4 = st.tabs(
                ["📊 Classification Report", "🔢 Confusion Matrix", "📈 Feature Importance", "📋 Per-Class Metrics"]
            )

            with sub1:
                report = results.get("classification_report", {})
                if report:
                    for key in ["macro avg", "weighted avg"]:
                        if key in report:
                            vals = report[key]
                            st.markdown(
                                f"**{key.title()}:** Precision={vals.get('precision', 0):.4f} | "
                                f"Recall={vals.get('recall', 0):.4f} | F1={vals.get('f1-score', 0):.4f}"
                            )
                    class_data = []
                    for cls, vals in report.items():
                        if cls not in ["accuracy", "macro avg", "weighted avg"] and isinstance(vals, dict):
                            class_data.append({
                                "Class": cls,
                                "Precision": round(vals.get("precision", 0), 4),
                                "Recall": round(vals.get("recall", 0), 4),
                                "F1-Score": round(vals.get("f1-score", 0), 4),
                                "Support": int(vals.get("support", 0)),
                            })
                    if class_data:
                        cr_df = pd.DataFrame(class_data).sort_values("F1-Score", ascending=False)
                        st.dataframe(cr_df, use_container_width=True, height=400)

            with sub2:
                cm = results.get("confusion_matrix", [])
                class_names = results.get("class_names", [])
                if cm and class_names:
                    n_show = min(15, len(class_names))
                    cm_arr = np.array(cm)[:n_show, :n_show]
                    labels = class_names[:n_show]

                    fig = px.imshow(
                        cm_arr, x=labels, y=labels,
                        color_continuous_scale="Teal",
                        labels=dict(x="Predicted", y="Actual", color="Count"),
                    )
                    fig.update_layout(
                        **plotly_dark_layout(
                            height=580,
                            title=f"Confusion Matrix (Top {n_show} Classes)",
                            xaxis={"tickangle": 45},
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Confusion matrix not available.")

            with sub3:
                importances = results.get("feature_importances", {})
                if importances:
                    imp_df = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance"])
                    imp_df = imp_df.sort_values("Importance", ascending=True)

                    fig = px.bar(
                        imp_df, x="Importance", y="Feature",
                        orientation="h", color="Importance",
                        color_continuous_scale="Tealgrn",
                    )
                    fig.update_layout(
                        **plotly_dark_layout(
                            height=max(420, len(imp_df) * 22),
                            title=f"{model_name} — Feature Importances",
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Feature importances not available.")

            with sub4:
                report = results.get("classification_report", {})
                if report:
                    class_data = []
                    for cls, vals in report.items():
                        if cls not in ["accuracy", "macro avg", "weighted avg"] and isinstance(vals, dict):
                            class_data.append({
                                "Class": cls,
                                "Precision": vals.get("precision", 0),
                                "Recall": vals.get("recall", 0),
                                "F1": vals.get("f1-score", 0),
                            })
                    if class_data:
                        pcd = pd.DataFrame(class_data).sort_values("F1", ascending=False)
                        fig = go.Figure()
                        fig.add_trace(go.Bar(name="Precision", x=pcd["Class"], y=pcd["Precision"]))
                        fig.add_trace(go.Bar(name="Recall", x=pcd["Class"], y=pcd["Recall"]))
                        fig.add_trace(go.Bar(name="F1", x=pcd["Class"], y=pcd["F1"]))
                        fig.update_layout(
                            **plotly_dark_layout(
                                barmode="group",
                                height=480,
                                title="Per-Class Metrics",
                                xaxis={"tickangle": 45},
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)

    # ── Export Section ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 Export Performance & Threat Report")
    e1, e2 = st.columns(2)
    alerts = st.session_state.get("security_alerts", [])
    with e1:
        st.download_button(
            "📄 Download CSV Report",
            data=generate_csv_report(dist, comparison, fl_results, alerts),
            file_name="model_performance_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with e2:
        st.download_button(
            "📑 Download PDF Report",
            data=generate_pdf_report(dist, comparison, fl_results, iso_info, alerts),
            file_name="model_performance_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
