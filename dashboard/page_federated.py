"""
Federated Learning page — visualize FL training rounds and client performance.
"""
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ARTIFACTS_DIR
from utils import load_json
from dashboard.theme import page_header, metric_card_html, plotly_dark_layout


def render():
    page_header("Federated Learning", "Privacy-preserving distributed model training with FedAvg", "🌐")

    fl_path = os.path.join(ARTIFACTS_DIR, "fl_results.json")
    fl_results = load_json(fl_path)

    if not fl_results:
        st.warning("⚠️ Federated learning results not found. Run the FL pipeline to generate real metrics.")
        if st.button("▶️ Run Federated Learning Simulation", use_container_width=False):
            with st.spinner("Running 3-client FedAvg simulation..."):
                from src.federated_learning import run_federated_learning
                _, fl_results = run_federated_learning()
            st.success("✅ Federated learning complete!")
            st.rerun()
        return

    # ── KPIs ─────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Clients", str(fl_results.get("num_clients", 0)), "🖥️", color="#22d3ee"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Rounds", str(fl_results.get("num_rounds", 0)), "🔄", color="#a78bfa"), unsafe_allow_html=True)
    with c3:
        st.markdown(
            metric_card_html("Global Accuracy", f"{fl_results.get('final_global_accuracy', 0):.2%}", "🎯", color="#22c55e"),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            metric_card_html("Global F1", f"{fl_results.get('final_global_f1', 0):.2%}", "📊", color="#14b8a6"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Training Progress", "🖥️ Client Performance", "📋 Round Details"])
    rounds = fl_results.get("rounds", [])

    with tab1:
        st.markdown("### Global Model Accuracy Over Rounds")
        if rounds:
            round_nums = [r["round"] for r in rounds]
            global_acc = [r["global_accuracy"] for r in rounds]
            global_f1 = [r["global_f1_score"] for r in rounds]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=round_nums, y=global_acc, mode="lines+markers",
                name="Accuracy", line=dict(color="#06b6d4", width=3), marker=dict(size=10),
            ))
            fig.add_trace(go.Scatter(
                x=round_nums, y=global_f1, mode="lines+markers",
                name="F1 Score", line=dict(color="#8b5cf6", width=3), marker=dict(size=10),
            ))
            fig.update_layout(
                **plotly_dark_layout(
                    height=400,
                    title="Global Model Performance per Round",
                    xaxis_title="Round",
                    yaxis_title="Score",
                    yaxis={"range": [0, 1.05]},
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        if len(rounds) > 1:
            improvement = rounds[-1]["global_accuracy"] - rounds[0]["global_accuracy"]
            st.markdown(f"""
            <div class="cyber-card">
                <div class="cyber-card-header">Convergence & Privacy Summary</div>
                <p style="margin-bottom:4px;">Accuracy delta across {len(rounds)} rounds: <strong>{improvement:+.4f}</strong></p>
                <p style="margin-bottom:0;">Final Global Accuracy: <strong>{rounds[-1]['global_accuracy']:.4f}</strong> | Raw IoT data never leaves client partitions.</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### Client Performance Comparison")
        if rounds:
            last_round = rounds[-1]
            client_data = last_round.get("client_metrics", [])

            if client_data:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[f"Client {r['client_id']}" for r in client_data],
                    y=[r["accuracy"] for r in client_data],
                    name="Accuracy", marker_color="#06b6d4",
                ))
                fig.add_trace(go.Bar(
                    x=[f"Client {r['client_id']}" for r in client_data],
                    y=[r["f1_score"] for r in client_data],
                    name="F1 Score", marker_color="#8b5cf6",
                ))
                fig.update_layout(**plotly_dark_layout(height=400, barmode="group", title="Client Performance (Final Round)"))
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Data Distribution Across Clients")
                fig2 = px.pie(
                    values=[r["samples"] for r in client_data],
                    names=[f"Client {r['client_id']}" for r in client_data],
                    hole=0.42,
                )
                fig2.update_layout(**plotly_dark_layout(height=350, title="Client Sample Distribution"))
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Client Accuracy Across Rounds")
            all_client_data = []
            for r in rounds:
                for cm in r.get("client_metrics", []):
                    all_client_data.append({
                        "Round": r["round"],
                        "Client": f"Client {cm['client_id']}",
                        "Accuracy": cm["accuracy"],
                        "F1": cm["f1_score"],
                    })
            if all_client_data:
                adf = pd.DataFrame(all_client_data)
                fig3 = px.line(adf, x="Round", y="Accuracy", color="Client", markers=True)
                fig3.update_layout(**plotly_dark_layout(height=400, title="Client Accuracy Over Rounds"))
                st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown("### Detailed Round Results")
        for r in rounds:
            with st.expander(f"🔄 Round {r['round']} — Global Acc: {r['global_accuracy']:.4f}"):
                st.markdown(f"**Global Accuracy:** {r['global_accuracy']:.4f} | **Global F1 Score:** {r['global_f1_score']:.4f}")
                if r.get("client_metrics"):
                    st.dataframe(pd.DataFrame(r["client_metrics"]), use_container_width=True)
