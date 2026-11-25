"""
IoT traffic replay and real-time threat detection using trained models.
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PROCESSED_DIR, MODELS_DIR, SELECTED_FEATURES,
    ATTACK_CATEGORIES, CATEGORY_SEVERITY,
)
from utils import logger, generate_alert


class ThreatDetector:
    """Loads trained models and performs predictions on IoT traffic."""

    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.fl_model = None
        self.iso_model = None
        self.le = None
        self.scaler = None
        self.loaded = False

    def load_models(self):
        """Load all trained models and preprocessing objects."""
        self.rf_model = joblib.load(os.path.join(MODELS_DIR, "random_forest.joblib"))
        self.xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgboost_model.joblib"))
        self.iso_model = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.joblib"))
        self.le = joblib.load(os.path.join(PROCESSED_DIR, "label_encoder.joblib"))
        self.scaler = joblib.load(os.path.join(PROCESSED_DIR, "scaler.joblib"))

        fl_path = os.path.join(MODELS_DIR, "federated_global_model.joblib")
        if os.path.exists(fl_path):
            self.fl_model = joblib.load(fl_path)

        self.loaded = True
        logger.info("All models loaded successfully")

    def _get_model(self, model_name: str):
        if model_name == "rf":
            return self.rf_model
        if model_name == "xgb":
            return self.xgb_model
        if model_name == "fl" and self.fl_model is not None:
            return self.fl_model
        return self.xgb_model

    def predict_single(self, features: dict, model_name: str = "rf",
                       already_scaled: bool = False) -> dict:
        """Predict on a single sample (dict of feature values)."""
        if not self.loaded:
            self.load_models()

        feature_values = np.array(
            [[float(features.get(f, 0.0)) for f in SELECTED_FEATURES]],
            dtype=np.float64,
        )
        feature_input = feature_values if already_scaled else self.scaler.transform(feature_values)

        model = self._get_model(model_name)
        pred_encoded = model.predict(feature_input)[0]
        pred_proba = model.predict_proba(feature_input)[0]
        confidence = float(np.max(pred_proba))
        pred_label = self.le.inverse_transform([pred_encoded])[0]

        anomaly_score = float(self.iso_model.score_samples(feature_input)[0])
        is_anomaly = bool(self.iso_model.predict(feature_input)[0] == -1)

        category = ATTACK_CATEGORIES.get(pred_label, "Unknown")
        severity = CATEGORY_SEVERITY.get(category, "Unknown")

        return {
            "prediction": pred_label,
            "category": category,
            "severity": severity,
            "confidence": round(confidence, 4),
            "anomaly_score": round(anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "probabilities": {
                self.le.inverse_transform([i])[0]: round(float(p), 4)
                for i, p in enumerate(pred_proba) if p > 0.01
            },
        }

    def predict_batch(self, df: pd.DataFrame, model_name: str = "rf",
                      already_scaled: bool = False) -> pd.DataFrame:
        """Predict on a DataFrame of samples."""
        if not self.loaded:
            self.load_models()

        X = df[SELECTED_FEATURES].values
        X_input = X if already_scaled else self.scaler.transform(X)

        model = self._get_model(model_name)
        preds = model.predict(X_input)
        pred_probas = model.predict_proba(X_input)
        confidences = np.max(pred_probas, axis=1)
        pred_labels = self.le.inverse_transform(preds)

        result_df = df.copy()
        result_df["predicted_label"] = pred_labels
        result_df["predicted_category"] = [
            ATTACK_CATEGORIES.get(l, "Unknown") for l in pred_labels
        ]
        result_df["severity"] = [
            CATEGORY_SEVERITY.get(ATTACK_CATEGORIES.get(l, "Unknown"), "Unknown")
            for l in pred_labels
        ]
        result_df["confidence"] = np.round(confidences.astype(float), 4)

        scores = self.iso_model.score_samples(X_input)
        anomalies = self.iso_model.predict(X_input)
        result_df["anomaly_score"] = scores
        result_df["is_anomaly"] = anomalies == -1

        return result_df

    def explain_prediction(self, features: dict, model_name: str = "rf",
                           already_scaled: bool = False) -> dict:
        """
        Explain why a sample was classified as benign or malicious using
        model feature importances weighted by standardized feature deviations.
        """
        if not self.loaded:
            self.load_models()

        pred_result = self.predict_single(
            features, model_name=model_name, already_scaled=already_scaled
        )
        model = self._get_model(model_name)

        feature_values = np.array(
            [[float(features.get(f, 0.0)) for f in SELECTED_FEATURES]],
            dtype=np.float64,
        )
        z_scores = feature_values[0] if already_scaled else self.scaler.transform(feature_values)[0]

        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            importances = np.ones(len(SELECTED_FEATURES)) / len(SELECTED_FEATURES)

        contributions = []
        for idx, feat in enumerate(SELECTED_FEATURES):
            imp = float(importances[idx])
            z_val = float(z_scores[idx])
            impact = imp * abs(z_val)
            contributions.append({
                "feature": feat,
                "z_score": round(z_val, 4),
                "global_importance": round(imp, 4),
                "local_impact": round(impact, 4),
            })

        contributions.sort(key=lambda x: x["local_impact"], reverse=True)
        top_drivers = contributions[:5]
        driver_names = ", ".join(d["feature"] for d in top_drivers[:3])

        if pred_result["category"] == "Benign":
            summary = (
                f"Classified as BenignTraffic (confidence {pred_result['confidence']:.2%}). "
                f"Key evaluated features ({driver_names}) remain aligned with normal IoT traffic baselines."
            )
        else:
            summary = (
                f"Classified as {pred_result['prediction']} ({pred_result['category']}, "
                f"severity {pred_result['severity']}, confidence {pred_result['confidence']:.2%}). "
                f"Primary contributing features: {driver_names} showed significant deviation from normal traffic."
            )

        return {
            "prediction_result": pred_result,
            "contributions": contributions,
            "summary": summary,
        }

    def replay_traffic(self, n_samples: int = 100, model_name: str = "rf") -> tuple:
        """Replay traffic from processed test dataset and generate alerts."""
        if not self.loaded:
            self.load_models()

        test_path = os.path.join(PROCESSED_DIR, "test_processed.parquet")
        if not os.path.exists(test_path):
            logger.error("Test data not found for replay")
            return pd.DataFrame(), []

        test_df = pd.read_parquet(test_path)
        samples = test_df.sample(
            n=min(n_samples, len(test_df)),
            random_state=int(time.time()) % 10000,
        )

        results = self.predict_batch(samples, model_name=model_name, already_scaled=True)
        alerts = []
        for _, row in results.iterrows():
            if row["predicted_category"] != "Benign":
                alert = generate_alert(
                    prediction=row["predicted_label"],
                    confidence=float(row["confidence"]),
                    features={f: float(row[f]) for f in SELECTED_FEATURES[:5]},
                )
                alert["status"] = "Active"
                alerts.append(alert)

        return results, alerts
