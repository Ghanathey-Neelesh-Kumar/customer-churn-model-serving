def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "model_loaded": True}


def test_model_info(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "customer-churn-classifier"
    assert "tenure_months" in body["features"]
