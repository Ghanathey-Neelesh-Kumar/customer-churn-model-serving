import json
from pathlib import Path


def payload(name: str) -> dict:
    return json.loads(Path(f"sample_requests/{name}").read_text(encoding="utf-8"))


def test_valid_prediction(client):
    response = client.post("/predict", json=payload("high_risk_customer.json"))
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["churn_probability"] <= 1
    assert body["risk_level"] in {"Low", "Medium", "High"}
    assert body["model_version"] == "1.0.0"
    assert response.headers.get("X-Request-ID")


def test_high_risk_scores_above_low_risk(client):
    high = client.post("/predict", json=payload("high_risk_customer.json")).json()
    low = client.post("/predict", json=payload("low_risk_customer.json")).json()
    assert high["churn_probability"] > low["churn_probability"]


def test_invalid_request_is_rejected(client):
    response = client.post("/predict", json=payload("invalid_customer.json"))
    assert response.status_code == 422
