import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from api.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models_loaded" in data


def test_crop_prediction():
    client = TestClient(app)
    payload = {
        "N": 90, "P": 42, "K": 43, "temperature": 20.88,
        "humidity": 82.0, "ph": 6.5, "rainfall": 202.9,
    }
    response = client.post("/predict/crop", json=payload)
    if response.status_code == 503:
        return  # models not present in CI without artifacts
    assert response.status_code == 200
    assert "crop" in response.json()


def test_fertilizer_prediction():
    client = TestClient(app)
    payload = {
        "temperature": 26, "humidity": 52, "moisture": 38,
        "soil_type": "Sandy", "crop_type": "Maize",
        "nitrogen": 37, "potassium": 0, "phosphorous": 0,
    }
    response = client.post("/predict/fertilizer", json=payload)
    if response.status_code == 503:
        return
    assert response.status_code == 200
    assert "fertilizer" in response.json()
