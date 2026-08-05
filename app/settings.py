"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Customer Churn Prediction API"
    app_version: str = "1.0.0"
    model_path: Path = Path("model/customer_churn_model.joblib")
    model_metadata_path: Path = Path("model/model_metadata.json")
    log_level: str = "INFO"
    medium_risk_threshold: float = Field(default=0.40, ge=0, le=1)
    high_risk_threshold: float = Field(default=0.70, ge=0, le=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_thresholds(self) -> "Settings":
        if self.medium_risk_threshold >= self.high_risk_threshold:
            raise ValueError("MEDIUM_RISK_THRESHOLD must be lower than HIGH_RISK_THRESHOLD")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
