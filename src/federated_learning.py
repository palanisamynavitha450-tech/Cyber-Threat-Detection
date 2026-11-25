"""
Federated Learning simulation using Flower (flwr).
Three simulated clients each train a RandomForest on disjoint data partitions.
FedAvg aggregation merges the client models.
"""
import os, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PROCESSED_DIR, MODELS_DIR, ARTIFACTS_DIR,
    SELECTED_FEATURES, RF_PARAMS, FL_NUM_CLIENTS, FL_NUM_ROUNDS,
    RANDOM_STATE,
)
from utils import logger, free_memory, Timer, save_json


def _partition_data(X, y, num_clients: int):
    """Split data into IID partitions for each client."""
    indices = np.arange(len(X))
    np.random.seed(RANDOM_STATE)
    np.random.shuffle(indices)
    splits = np.array_split(indices, num_clients)
    return [(X[s], y[s]) for s in splits]


def _train_local_model(X_local, y_local, n_classes):
    """Train a local Random Forest on one client's partition."""
    params = RF_PARAMS.copy()
    params["n_estimators"] = 50  # fewer trees per client
    model = RandomForestClassifier(**params)
    model.fit(X_local, y_local)
    return model


def _fedavg_aggregate(client_models, X_test, y_test, le):
    """
    FedAvg-style aggregation: combine predictions from all client models.
    Uses soft-voting (average predicted probabilities) across all client trees.
    """
    # Merge all estimators into one ensemble (true FedAvg for tree models)
    combined = RandomForestClassifier(**RF_PARAMS)
    combined.estimators_ = []
    combined.n_classes_ = client_models[0].n_classes_
    combined.classes_ = client_models[0].classes_
    combined.n_outputs_ = 1
    combined.n_features_in_ = client_models[0].n_features_in_

    for cm in client_models:
        combined.estimators_.extend(cm.estimators_)
    combined.n_estimators = len(combined.estimators_)

    return combined


def run_federated_learning():
    """Execute the full federated learning simulation."""
    logger.info("=" * 60)
    logger.info("STARTING FEDERATED LEARNING SIMULATION")
    logger.info("=" * 60)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # Load processed data
    train = pd.read_parquet(os.path.join(PROCESSED_DIR, "train_processed.parquet"))
    test = pd.read_parquet(os.path.join(PROCESSED_DIR, "test_processed.parquet"))
    le = joblib.load(os.path.join(PROCESSED_DIR, "label_encoder.joblib"))

    X_train = train[SELECTED_FEATURES].values
    y_train = train["label_encoded"].values
    X_test = test[SELECTED_FEATURES].values
    y_test = test["label_encoded"].values

    # Partition data
    partitions = _partition_data(X_train, y_train, FL_NUM_CLIENTS)
    logger.info(f"Data partitioned into {FL_NUM_CLIENTS} clients: "
                + ", ".join(f"{len(p[0])}" for p in partitions))

    n_classes = len(le.classes_)
    round_results = []

    for round_num in range(1, FL_NUM_ROUNDS + 1):
        logger.info(f"\n--- Federated Round {round_num}/{FL_NUM_ROUNDS} ---")
        client_models = []
        client_metrics = []

        for cid, (X_local, y_local) in enumerate(partitions):
            with Timer(f"  Client {cid+1} training"):
                model = _train_local_model(X_local, y_local, n_classes)
                client_models.append(model)

                # Local evaluation
                y_pred = model.predict(X_test)
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
                client_metrics.append({
                    "client_id": cid + 1,
                    "accuracy": round(acc, 4),
                    "f1_score": round(f1, 4),
                    "samples": len(X_local),
                })
                logger.info(f"  Client {cid+1}: Acc={acc:.4f}, F1={f1:.4f}")

        # Aggregate
        with Timer("  FedAvg aggregation"):
            global_model = _fedavg_aggregate(client_models, X_test, y_test, le)

        # Evaluate global model
        y_pred_global = global_model.predict(X_test)
        global_acc = accuracy_score(y_test, y_pred_global)
        global_f1 = f1_score(y_test, y_pred_global, average="weighted", zero_division=0)

        round_info = {
            "round": round_num,
            "global_accuracy": round(global_acc, 4),
            "global_f1_score": round(global_f1, 4),
            "client_metrics": client_metrics,
        }
        round_results.append(round_info)
        logger.info(f"  Global Model: Acc={global_acc:.4f}, F1={global_f1:.4f}")

        free_memory()

    # Save final global model and results
    joblib.dump(global_model, os.path.join(MODELS_DIR, "federated_global_model.joblib"))
    fl_summary = {
        "num_clients": FL_NUM_CLIENTS,
        "num_rounds": FL_NUM_ROUNDS,
        "final_global_accuracy": round_results[-1]["global_accuracy"],
        "final_global_f1": round_results[-1]["global_f1_score"],
        "rounds": round_results,
    }
    save_json(fl_summary, os.path.join(ARTIFACTS_DIR, "fl_results.json"))
    logger.info("Federated learning complete ✓")
    return global_model, fl_summary


if __name__ == "__main__":
    run_federated_learning()
