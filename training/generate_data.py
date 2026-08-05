"""Generate a deterministic synthetic customer-churn dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/customer_churn.csv"))
    return parser.parse_args()


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    tenure = rng.integers(0, 73, args.rows)
    monthly = np.clip(rng.normal(72, 25, args.rows), 18, 140).round(2)
    support_calls = np.clip(rng.poisson(2.4, args.rows), 0, 15)
    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"],
        size=args.rows,
        p=[0.57, 0.25, 0.18],
    )
    internet = rng.choice(["DSL", "Fiber optic", "No"], args.rows, p=[0.35, 0.50, 0.15])
    payment = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        args.rows,
        p=[0.35, 0.18, 0.24, 0.23],
    )

    logit = (
        -1.0
        - 0.035 * tenure
        + 0.014 * (monthly - 70)
        + 0.33 * support_calls
        + 1.05 * (contract == "Month-to-month")
        - 0.55 * (contract == "Two year")
        + 0.48 * (internet == "Fiber optic")
        + 0.42 * (payment == "Electronic check")
    )
    probabilities = sigmoid(logit)
    churn = rng.binomial(1, probabilities)

    frame = pd.DataFrame(
        {
            "tenure_months": tenure,
            "monthly_charges": monthly,
            "support_calls": support_calls,
            "contract_type": contract,
            "internet_service": internet,
            "payment_method": payment,
            "churn": churn,
        }
    )

    # Add a small amount of missing data so the pipeline demonstrates imputation.
    for column in ["monthly_charges", "internet_service"]:
        indexes = rng.choice(frame.index, size=max(1, args.rows // 100), replace=False)
        frame.loc[indexes, column] = np.nan

    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Created {len(frame)} rows at {args.output}")
    print(f"Churn rate: {frame['churn'].mean():.3f}")


if __name__ == "__main__":
    main()
