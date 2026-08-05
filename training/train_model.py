"""Train and persist a complete preprocessing-and-classification pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURES = [
    "tenure_months",
    "monthly_charges",
    "support_calls",
    "contract_type",
    "internet_service",
    "payment_method",
]
NUMERIC = ["tenure_months", "monthly_charges", "support_calls"]
CATEGORICAL = ["contract_type", "internet_service", "payment_method"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/customer_churn.csv"))
    parser.add_argument("--model", type=Path, default=Path("model/customer_churn_model.joblib"))
    parser.add_argument("--metadata", type=Path, default=Path("model/model_metadata.json"))
    parser.add_argument("--metrics", type=Path, default=Path("model/evaluation_metrics.json"))
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    if not args.data.exists():
        raise FileNotFoundError("Dataset missing. Run: python training/generate_data.py")

    data = pd.read_csv(args.data)
    x = data[FEATURES]
    y = data["churn"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.20, random_state=42, stratify=y
    )

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric_pipeline, NUMERIC),
            ("categorical", categorical_pipeline, CATEGORICAL),
        ]
    )
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "test_rows": int(len(x_test)),
    }

    args.model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, args.model, compress=3)

    metadata = {
        "model_name": "customer-churn-classifier",
        "model_version": "1.0.0",
        "algorithm": "LogisticRegression",
        "target": "churn",
        "features": FEATURES,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "scikit_learn_version": sklearn.__version__,
        "artifact_sha256": file_sha256(args.model),
        "educational_use_only": True,
    }
    args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    args.metrics.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model saved to {args.model}")
    print(f"Metadata saved to {args.metadata}")
    for name, value in metrics.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
