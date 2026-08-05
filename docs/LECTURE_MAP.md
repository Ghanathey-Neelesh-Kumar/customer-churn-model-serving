# Instructor lecture map

This document maps repository files to the compressed 30-lecture deployment track.

## Section 6

### Lecture 5 — Repository walkthrough
Show `README.md`, `app/`, `training/`, `sample_requests/`, `tests/`, `vm/`, `Dockerfile`, and `kubernetes/`.

### Lecture 6 — Prepare and validate the model artifact
Use:

```bash
python training/generate_data.py
python training/train_model.py
python training/validate_model.py
```

Explain `model_metadata.json`, checksum validation, trusted artifacts and the complete pipeline.

### Lecture 7 — Build the FastAPI service
Explain in this order:

1. `app/settings.py`
2. `app/schemas.py`
3. `app/model_loader.py`
4. `app/predictor.py`
5. `app/main.py`

### Lecture 8 — Test the service
Run:

```bash
uvicorn app.main:app --reload
pytest -q
python scripts/test_api.py
```

Demonstrate `/docs`, `/health`, `/ready`, `/model-info`, valid prediction and HTTP 422 validation.

## Section 7

Use `vm/README.md`, `vm/customer-churn-api.service`, `vm/nginx.conf`, `vm/deploy.sh`, and `vm/user-data.sh`.

Record manual deployment before showing automation. Never reveal credentials in terminal history.

## Section 8

Use `Dockerfile`, `.dockerignore`, `compose.yaml`, immutable tags and ECR commands from the main README.

## Section 9

Use manifests in this order:

1. namespace
2. configmap
3. deployment
4. service
5. HPA
6. Gateway
7. HTTPRoute

Explain startup vs readiness vs liveness before applying the Deployment.
