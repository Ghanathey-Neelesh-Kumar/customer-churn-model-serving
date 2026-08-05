"""Validate the persisted model independently of the web API."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from app.model_loader import load_model

MODEL_PATH = Path("model/customer_churn_model.joblib")
METADATA_PATH = Path("model/model_metadata.json")

EXAMPLES = pd.DataFrame(
    [
        {
            "tenure_months": 3,
            "monthly_charges": 105.0,
            "support_calls": 8,
            "contract_type": "Month-to-month",
            "internet_service": "Fiber optic",
            "payment_method": "Electronic check",
        },
        {
            "tenure_months": 58,
            "monthly_charges": 55.0,
            "support_calls": 1,
            "contract_type": "Two year",
            "internet_service": "DSL",
            "payment_method": "Bank transfer",
        },
    ]
)


def main() -> None:
    loaded = load_model(MODEL_PATH, METADATA_PATH)
    probabilities = loaded.pipeline.predict_proba(EXAMPLES)[:, 1]
    print("Model validation succeeded")
    print(f"Model: {loaded.metadata['model_name']} {loaded.metadata['model_version']}")
    print(f"High-risk example probability: {probabilities[0]:.4f}")
    print(f"Low-risk example probability:  {probabilities[1]:.4f}")
    if not probabilities[0] > probabilities[1]:
        raise RuntimeError("Expected the high-risk example to score above the low-risk example")


if __name__ == "__main__":
    main()
