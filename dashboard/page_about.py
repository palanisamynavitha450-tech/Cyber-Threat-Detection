"""
About Project page — project documentation, dataset summary, tech stack, and architecture.
"""
import streamlit as st
from dashboard.theme import page_header


def render():
    page_header("About Project", "Project documentation and technical architecture", "ℹ️")

    st.markdown("""
    <div class="cyber-card">
        <div class="cyber-card-header">Project Title</div>
        <h2 style="color: #f1f5f9; margin-top: 8px; margin-bottom: 4px;">
            Privacy-Preserving Intelligent Cyber Threat Detection<br>
            Using Federated Learning and Anomaly Detection
        </h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-header">📋 Project Description</div>
            <p style="color: #cbd5e1; line-height: 1.75; margin-top: 10px;">
                This platform implements an AI-powered cybersecurity system for IoT networks
                that combines supervised multi-class threat classification (Random Forest & XGBoost),
                unsupervised zero-day anomaly detection (Isolation Forest), and privacy-preserving
                Federated Learning (FedAvg across 3 simulated IoT clients).
            </p>
            <p style="color: #cbd5e1; line-height: 1.75; margin-bottom: 0;">
                The federated learning architecture enables collaborative model training across
                distributed IoT edge nodes without sharing raw network traffic, preserving data privacy
                while achieving high detection accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-header">📊 Dataset (CICIoT2023)</div>
            <p style="color: #cbd5e1; line-height: 1.75; margin-top: 10px; margin-bottom: 0;">
                <strong>CICIoT2023</strong> — Comprehensive IoT attack dataset from the Canadian Institute for Cybersecurity:<br><br>
                • 5.49M+ raw training flow records (chunk-processed for 8 GB RAM)<br>
                • 31 selected high-signal network flow features + label<br>
                • 34 traffic classes grouped into 9 threat categories<br>
                • Train / Test / Validation CSV splits
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-header">🛠️ Technology Stack</div>
            <div style="margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">🐍</span><br>
                    <span style="color: #22d3ee; font-size: 0.85rem;">Python 3</span>
                </div>
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">🌲</span><br>
                    <span style="color: #22d3ee; font-size: 0.85rem;">Random Forest</span>
                </div>
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">🚀</span><br>
                    <span style="color: #a78bfa; font-size: 0.85rem;">XGBoost</span>
                </div>
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">🔔</span><br>
                    <span style="color: #14b8a6; font-size: 0.85rem;">Isolation Forest</span>
                </div>
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">🌐</span><br>
                    <span style="color: #22d3ee; font-size: 0.85rem;">Flower FL (FedAvg)</span>
                </div>
                <div class="cyber-card" style="padding: 10px; text-align: center; margin-bottom:0;">
                    <span style="font-size: 1.4rem;">📊</span><br>
                    <span style="color: #a78bfa; font-size: 0.85rem;">Streamlit & Plotly</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-header">🔑 Key Capabilities</div>
            <ul style="color: #cbd5e1; line-height: 1.85; margin-top: 10px; margin-bottom: 0;">
                <li>Multi-model threat classification & anomaly scoring</li>
                <li>Privacy-preserving 3-client Federated Learning</li>
                <li>Simulated dataset-based IoT traffic replay</li>
                <li>Live Security Alert Center & PDF/CSV report export</li>
                <li>Explainable AI feature attribution</li>
                <li>System Health & artifact monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
