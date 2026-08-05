"""Prediction logic kept separate from HTTP endpoint code."""

from __future__ import annotations

import pandas as pd

from app.model_loader import LoadedModel
from app.schemas import CustomerFeatures


def risk_level(probability: float, medium_threshold: float, high_threshold: float) -> str:
    if probability >= high_threshold:
        return "High"
    if probability >= medium_threshold:
        return "Medium"
    return "Low"


def predict_customer(
    loaded_model: LoadedModel,
    customer: CustomerFeatures,
    medium_threshold: float,
    high_threshold: float,
) -> dict[str, object]:
    frame = pd.DataFrame([customer.model_dump()])
    probability = float(loaded_model.pipeline.predict_proba(frame)[0, 1])
    prediction = (
        "Customer may churn" if probability >= 0.50 else "Customer likely to stay"
    )

    return {
        "prediction": prediction,
        "churn_probability": round(probability, 4),
        "risk_level": risk_level(probability, medium_threshold, high_threshold),
    }
