"""
System Health Monitor — real file/model/dataset availability, timestamps, and runtime environment.
"""
import os
import sys
import platform
from datetime import datetime
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TRAIN_CSV, TEST_CSV, VALIDATION_CSV,
    PROCESSED_DIR, MODELS_DIR, ARTIFACTS_DIR,
)
from utils import load_json
from dashboard.theme import page_header, metric_card_html, status_pill


def _file_info(path: str) -> dict:
    exists = os.path.exists(path)
    if not exists:
        return {"exists": False, "size_mb": 0.0, "modified": "N/A"}
    size_mb = os.path.getsize(path) / (1024 * 1024)
    mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
    return {"exists": True, "size_mb": round(size_mb, 2), "modified": mtime}


def render():
    page_header("System Health", "Real-time verification of models, datasets, artifacts, and environment", "🩺")

    model_files = {
        "Random Forest": os.path.join(MODELS_DIR, "random_forest.joblib"),
        "XGBoost": os.path.join(MODELS_DIR, "xgboost_model.joblib"),
        "Isolation Forest": os.path.join(MODELS_DIR, "isolation_forest.joblib"),
        "Federated Global Model": os.path.join(MODELS_DIR, "federated_global_model.joblib"),
    }
    data_files = {
        "Raw Train CSV": TRAIN_CSV,
        "Raw Test CSV": TEST_CSV,
        "Raw Validation CSV": VALIDATION_CSV,
        "Processed Train Parquet": os.path.join(PROCESSED_DIR, "train_processed.parquet"),
        "Processed Test Parquet": os.path.join(PROCESSED_DIR, "test_processed.parquet"),
        "Label Encoder": os.path.join(PROCESSED_DIR, "label_encoder.joblib"),
        "Standard Scaler": os.path.join(PROCESSED_DIR, "scaler.joblib"),
    }

    models_ok = sum(1 for p in model_files.values() if os.path.exists(p))
    data_ok = sum(1 for p in data_files.values() if os.path.exists(p))
    iso_info = load_json(os.path.join(ARTIFACTS_DIR, "iso_forest_info.json"))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Models Ready", f"{models_ok} / {len(model_files)}", "🤖", color="#22c55e" if models_ok == len(model_files) else "#f97316"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("Data Assets", f"{data_ok} / {len(data_files)}", "📂", color="#22d3ee"), unsafe_allow_html=True)
    with c3:
        iso_thresh = f"{iso_info.get('threshold', 0):.4f}" if iso_info else "N/A"
        st.markdown(metric_card_html("Anomaly Threshold", iso_thresh, "🔔", color="#a78bfa"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card_html("Python Runtime", platform.python_version(), "🐍", color="#14b8a6"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### 🤖 Model Loading & Training Timestamps")
        for name, path in model_files.items():
            info = _file_info(path)
            pill = status_pill("AVAILABLE" if info["exists"] else "MISSING", info["exists"])
            st.markdown(f"""
            <div class="cyber-card" style="padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:#f1f5f9;">{name}</strong>
                    {pill}
                </div>
                <div style="color:#94a3b8; font-size:0.8rem; margin-top:6px;">
                    Size: {info['size_mb']} MB | Last Updated: {info['modified']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📂 Dataset & Preprocessing Availability")
        for name, path in data_files.items():
            info = _file_info(path)
            pill = status_pill("AVAILABLE" if info["exists"] else "MISSING", info["exists"])
            st.markdown(f"""
            <div class="cyber-card" style="padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:#f1f5f9;">{name}</strong>
                    {pill}
                </div>
                <div style="color:#94a3b8; font-size:0.8rem; margin-top:6px;">
                    Size: {info['size_mb']} MB | Last Updated: {info['modified']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Runtime Environment")
    st.markdown(f"""
    <div class="cyber-card">
        <div class="cyber-card-header">SYSTEM INFORMATION</div>
        <p style="margin-bottom:4px;"><strong>OS:</strong> {platform.system()} {platform.release()} ({platform.machine()})</p>
        <p style="margin-bottom:4px;"><strong>Streamlit Version:</strong> {st.__version__}</p>
        <p style="margin-bottom:0;"><strong>Anomaly Detector Status:</strong> {'Active (Trained on ' + str(iso_info.get('benign_samples', 0)) + ' benign samples)' if iso_info else 'Not calibrated'}</p>
    </div>
    """, unsafe_allow_html=True)
