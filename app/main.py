"""FastAPI application for customer churn inference."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status

from app.model_loader import LoadedModel, load_model
from app.predictor import predict_customer
from app.schemas import (
    CustomerFeatures,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
    ReadinessResponse,
)
from app.settings import get_settings

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("customer-churn-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading trusted model artifact from %s", settings.model_path)
    app.state.loaded_model = load_model(
        settings.model_path,
        settings.model_metadata_path,
    )
    logger.info("Model loaded successfully")
    yield
    app.state.loaded_model = None


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Educational online-inference API for a synthetic customer-churn model. "
        "Do not use for real customer decisions."
    ),
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request failure request_id=%s", request_id)
        raise
    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Operations"])
def ready(request: Request) -> ReadinessResponse:
    loaded = isinstance(getattr(request.app.state, "loaded_model", None), LoadedModel)
    if not loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return ReadinessResponse(status="ready", model_loaded=True)


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Model"])
def model_info(request: Request) -> ModelInfoResponse:
    loaded_model: LoadedModel | None = getattr(request.app.state, "loaded_model", None)
    if loaded_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    metadata = loaded_model.metadata
    return ModelInfoResponse(
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
        algorithm=metadata["algorithm"],
        target=metadata["target"],
        features=metadata["features"],
        trained_at_utc=metadata["trained_at_utc"],
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict(customer: CustomerFeatures, request: Request) -> PredictionResponse:
    loaded_model: LoadedModel | None = getattr(
        request.app.state,
        "loaded_model",
        None,
    )

    if loaded_model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    result = predict_customer(
        loaded_model,
        customer,
        settings.medium_risk_threshold,
        settings.high_risk_threshold,
    )

    request_id = request.state.request_id

    return PredictionResponse(
        request_id=request_id,
        prediction=result["prediction"],
        churn_probability=result["churn_probability"],
        risk_level=result["risk_level"],
        model_name=loaded_model.metadata["model_name"],
        model_version=loaded_model.metadata["model_version"],
    )
   
