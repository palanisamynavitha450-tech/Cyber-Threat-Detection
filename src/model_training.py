"""
Model training — Random Forest, XGBoost, Isolation Forest.
"""
import os, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PROCESSED_DIR, MODELS_DIR, ARTIFACTS_DIR,
    SELECTED_FEATURES, LABEL_COLUMN,
    RF_PARAMS, XGB_PARAMS, ISO_FOREST_PARAMS, RANDOM_STATE,
)
from utils import logger, free_memory, Timer, save_json


def load_processed_data():
    """Load preprocessed parquet files."""
    train = pd.read_parquet(os.path.join(PROCESSED_DIR, "train_processed.parquet"))
    test = pd.read_parquet(os.path.join(PROCESSED_DIR, "test_processed.parquet"))
    le = joblib.load(os.path.join(PROCESSED_DIR, "label_encoder.joblib"))
    return train, test, le


def _get_xy(df, features=None):
    if features is None:
        features = SELECTED_FEATURES
    X = df[features].values
    y = df["label_encoded"].values
    return X, y


def evaluate_model(model, X_test, y_test, le, model_name: str) -> dict:
    """Compute metrics and return results dict."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # Per-class report
    valid_mask = y_test >= 0
    report = classification_report(
        y_test[valid_mask], y_pred[valid_mask],
        target_names=le.classes_, output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_test[valid_mask], y_pred[valid_mask]).tolist()

    results = {
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "classification_report": report,
        "confusion_matrix": cm,
        "num_classes": len(le.classes_),
        "class_names": le.classes_.tolist(),
    }
    logger.info(f"{model_name}: Acc={acc:.4f}  Prec={prec:.4f}  "
                f"Rec={rec:.4f}  F1={f1:.4f}")
    return results


def train_random_forest(X_train, y_train, X_test, y_test, le):
    """Train and evaluate Random Forest."""
    logger.info("Training Random Forest…")
    with Timer("Random Forest training"):
        rf = RandomForestClassifier(**RF_PARAMS)
        rf.fit(X_train, y_train)

    results = evaluate_model(rf, X_test, y_test, le, "Random Forest")

    # Feature importances
    importances = dict(zip(SELECTED_FEATURES,
                           rf.feature_importances_.tolist()))
    results["feature_importances"] = importances

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(rf, os.path.join(MODELS_DIR, "random_forest.joblib"))
    save_json(results, os.path.join(ARTIFACTS_DIR, "rf_results.json"))
    free_memory()
    return rf, results


def train_xgboost(X_train, y_train, X_test, y_test, le):
    """Train and evaluate XGBoost."""
    from xgboost import XGBClassifier
    logger.info("Training XGBoost…")

    params = XGB_PARAMS.copy()
    params["num_class"] = len(le.classes_)
    params["objective"] = "multi:softprob"

    with Timer("XGBoost training"):
        xgb = XGBClassifier(**params)
        xgb.fit(X_train, y_train, verbose=False)

    results = evaluate_model(xgb, X_test, y_test, le, "XGBoost")

    importances = dict(zip(SELECTED_FEATURES,
                           xgb.feature_importances_.tolist()))
    results["feature_importances"] = importances

    joblib.dump(xgb, os.path.join(MODELS_DIR, "xgboost_model.joblib"))
    save_json(results, os.path.join(ARTIFACTS_DIR, "xgb_results.json"))
    free_memory()
    return xgb, results


def train_isolation_forest(X_train, y_train_labels):
    """
    Train Isolation Forest on benign traffic for anomaly detection.
    Returns the model and a threshold.
    """
    logger.info("Training Isolation Forest (anomaly detection)…")

    # Train on benign samples only
    benign_mask = y_train_labels == "BenignTraffic"
    X_benign = X_train[benign_mask]

    if len(X_benign) == 0:
        logger.warning("No benign samples found; training on all data")
        X_benign = X_train

    with Timer("Isolation Forest training"):
        iso = IsolationForest(**ISO_FOREST_PARAMS)
        iso.fit(X_benign)

    # Compute scores on training data for threshold calibration
    scores = iso.score_samples(X_benign)
    threshold = float(np.percentile(scores, 5))  # 5th percentile

    joblib.dump(iso, os.path.join(MODELS_DIR, "isolation_forest.joblib"))
    save_json({"threshold": threshold, "benign_samples": int(len(X_benign))},
              os.path.join(ARTIFACTS_DIR, "iso_forest_info.json"))

    logger.info(f"Isolation Forest trained on {len(X_benign)} benign samples, "
                f"threshold={threshold:.4f}")
    free_memory()
    return iso, threshold


def run_training():
    """Full training pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING MODEL TRAINING PIPELINE")
    logger.info("=" * 60)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    train_df, test_df, le = load_processed_data()
    X_train, y_train = _get_xy(train_df)
    X_test, y_test = _get_xy(test_df)

    # Random Forest
    rf, rf_results = train_random_forest(X_train, y_train, X_test, y_test, le)

    # XGBoost
    xgb, xgb_results = train_xgboost(X_train, y_train, X_test, y_test, le)

    # Isolation Forest (uses unscaled labels for benign filtering)
    iso, threshold = train_isolation_forest(X_train, train_df[LABEL_COLUMN].values)

    # Comparison summary
    comparison = {
        "Random Forest": {k: rf_results[k] for k in
                          ["accuracy", "precision", "recall", "f1_score"]},
        "XGBoost": {k: xgb_results[k] for k in
                    ["accuracy", "precision", "recall", "f1_score"]},
    }
    save_json(comparison, os.path.join(ARTIFACTS_DIR, "model_comparison.json"))

    logger.info("All models trained and saved ✓")
    return rf, xgb, iso


if __name__ == "__main__":
    run_training()
