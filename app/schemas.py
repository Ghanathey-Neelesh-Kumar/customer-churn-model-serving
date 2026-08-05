"""Typed request and response schemas for the prediction API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ContractType = Literal["Month-to-month", "One year", "Two year"]
InternetService = Literal["DSL", "Fiber optic", "No"]
PaymentMethod = Literal[
    "Electronic check",
    "Mailed check",
    "Bank transfer",
    "Credit card",
]


class CustomerFeatures(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tenure_months": 3,
                "monthly_charges": 105.0,
                "support_calls": 8,
                "contract_type": "Month-to-month",
                "internet_service": "Fiber optic",
                "payment_method": "Electronic check",
            }
        }
    )

    tenure_months: int = Field(ge=0, le=120)
    monthly_charges: float = Field(ge=0, le=1000)
    support_calls: int = Field(ge=0, le=100)
    contract_type: ContractType
    internet_service: InternetService
    payment_method: PaymentMethod


class PredictionResponse(BaseModel):
    request_id: str
    prediction: Literal["Customer may churn", "Customer likely to stay"]
    churn_probability: float = Field(ge=0, le=1)
    risk_level: Literal["Low", "Medium", "High"]
    model_name: str
    model_version: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    algorithm: str
    target: str
    features: list[str]
    trained_at_utc: str
