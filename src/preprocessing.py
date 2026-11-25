"""
Data preprocessing pipeline for CICIoT2023 dataset.
Memory-efficient chunk-based loading, cleaning, encoding, and feature selection.
"""
import os, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TRAIN_CSV, TEST_CSV, VALIDATION_CSV,
    PROCESSED_DIR, LABEL_COLUMN, FEATURE_COLUMNS,
    SELECTED_FEATURES, CHUNK_SIZE, SAMPLE_SIZE, TEST_SAMPLE_SIZE,
    ATTACK_CATEGORIES, RANDOM_STATE,
)
from utils import logger, reduce_mem_usage, free_memory, Timer, save_json


def load_data_chunked(csv_path: str, max_rows: int = None,
                      features: list = None) -> pd.DataFrame:
    """Load CSV in chunks, returning a sampled DataFrame."""
    if features is None:
        features = SELECTED_FEATURES
    cols_to_read = features + [LABEL_COLUMN]
    chunks = []
    rows_read = 0
    for chunk in pd.read_csv(csv_path, usecols=cols_to_read,
                             chunksize=CHUNK_SIZE, low_memory=False):
        chunk = reduce_mem_usage(chunk)
        chunks.append(chunk)
        rows_read += len(chunk)
        if max_rows and rows_read >= max_rows:
            break
    df = pd.concat(chunks, ignore_index=True)
    if max_rows and len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=RANDOM_STATE).reset_index(drop=True)
    free_memory()
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values, infinities, and duplicates."""
    initial = len(df)
    # Replace inf with NaN, then fill NaN with column median (Pandas 3 CoW-safe)
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(0.0 if pd.isna(median_val) else median_val)
    df = df.drop_duplicates()
    cleaned = initial - len(df)
    logger.info(f"Cleaned: removed {cleaned} duplicate rows, {initial} → {len(df)}")
    return df


def add_attack_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add a coarse attack category column."""
    df["attack_category"] = df[LABEL_COLUMN].map(ATTACK_CATEGORIES).fillna("Unknown")
    return df


def encode_labels(df: pd.DataFrame, le: LabelEncoder = None):
    """Encode the label column; returns (df, label_encoder)."""
    if le is None:
        le = LabelEncoder()
        df["label_encoded"] = le.fit_transform(df[LABEL_COLUMN])
    else:
        # Handle unseen labels gracefully
        known = set(le.classes_)
        df["label_encoded"] = df[LABEL_COLUMN].apply(
            lambda x: le.transform([x])[0] if x in known else -1
        )
    return df, le


def scale_features(df: pd.DataFrame, scaler: StandardScaler = None,
                   features: list = None):
    """Standard-scale numeric features; returns (df, scaler)."""
    if features is None:
        features = SELECTED_FEATURES
    if scaler is None:
        scaler = StandardScaler()
        df[features] = scaler.fit_transform(df[features])
    else:
        df[features] = scaler.transform(df[features])
    return df, scaler


def get_class_distribution(df: pd.DataFrame) -> dict:
    """Return label and category distributions."""
    label_dist = df[LABEL_COLUMN].value_counts().to_dict()
    cat_dist = {}
    if "attack_category" in df.columns:
        cat_dist = df["attack_category"].value_counts().to_dict()
    return {"label_distribution": label_dist, "category_distribution": cat_dist}


def run_preprocessing(save: bool = True):
    """Full preprocessing pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING DATA PREPROCESSING PIPELINE")
    logger.info("=" * 60)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # --- Train data ---
    with Timer("Load training data"):
        train_df = load_data_chunked(TRAIN_CSV, max_rows=SAMPLE_SIZE)
    logger.info(f"Training samples loaded: {len(train_df)}")

    with Timer("Clean training data"):
        train_df = clean_data(train_df)

    train_df = add_attack_category(train_df)
    dist = get_class_distribution(train_df)
    logger.info(f"Training classes: {len(dist['label_distribution'])}")

    with Timer("Encode labels"):
        train_df, le = encode_labels(train_df)

    with Timer("Scale features"):
        train_df, scaler = scale_features(train_df)

    # --- Test data ---
    with Timer("Load test data"):
        test_df = load_data_chunked(TEST_CSV, max_rows=TEST_SAMPLE_SIZE)
    test_df = clean_data(test_df)
    test_df = add_attack_category(test_df)
    test_df, _ = encode_labels(test_df, le=le)
    test_df, _ = scale_features(test_df, scaler=scaler)

    if save:
        with Timer("Save processed data"):
            train_df.to_parquet(os.path.join(PROCESSED_DIR, "train_processed.parquet"),
                                index=False)
            test_df.to_parquet(os.path.join(PROCESSED_DIR, "test_processed.parquet"),
                               index=False)
            joblib.dump(le, os.path.join(PROCESSED_DIR, "label_encoder.joblib"))
            joblib.dump(scaler, os.path.join(PROCESSED_DIR, "scaler.joblib"))
            save_json(dist, os.path.join(PROCESSED_DIR, "class_distribution.json"))

            # Save feature names
            save_json({"features": SELECTED_FEATURES},
                      os.path.join(PROCESSED_DIR, "feature_names.json"))

    logger.info("Preprocessing complete ✓")
    free_memory()
    return train_df, test_df, le, scaler


if __name__ == "__main__":
    run_preprocessing()
