"""Load and validate a trusted model artifact once during application startup."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib


@dataclass(frozen=True)
class LoadedModel:
    pipeline: Any
    metadata: dict[str, Any]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_model(model_path: Path, metadata_path: Path) -> LoadedModel:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {model_path}. Run: python training/train_model.py"
        )
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Model metadata not found at {metadata_path}. Run: python training/train_model.py"
        )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected_sha256 = metadata.get("artifact_sha256")
    actual_sha256 = sha256_file(model_path)
    if expected_sha256 and expected_sha256 != actual_sha256:
        raise ValueError("Model artifact checksum does not match model_metadata.json")

    # Security: joblib is pickle-based. Load only artifacts produced by this trusted project.
    pipeline = joblib.load(model_path)

    for method_name in ("predict", "predict_proba"):
        if not hasattr(pipeline, method_name):
            raise TypeError(f"Loaded model does not provide required method: {method_name}")

    return LoadedModel(pipeline=pipeline, metadata=metadata)
