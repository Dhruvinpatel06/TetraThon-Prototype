import pytest
from fastapi.testclient import TestClient
from App.main import app

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert "adapters" in data

def test_api_locations_endpoint():
    response = client.get("/api/locations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "latitude" in data[0]

def test_api_crops_endpoint():
    response = client.get("/api/crops")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]

def test_api_advisory_post():
    payload = {
        "location_name": "Anand",
        "crop_name": "Cotton",
        "sowing_date": "2026-05-15",
        "weather_observation": "hot_and_dry"
    }
    response = client.post("/api/advisory", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "advisories" in data
    assert "session_id" in data

def test_api_post_harvest_post():
    payload = {
        "crop_name": "Cotton",
        "quantity_quintals": 10.0,
        "storage_condition": "warehouse",
        "location_name": "Anand"
    }
    response = client.post("/api/post-harvest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data
    assert "expected_return" in data

def test_api_price_history_endpoint():
    response = client.get("/api/price-history?crop=Cotton&location=Ahmedabad")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Cotton"
    assert "history" in data

def test_api_spoilage_curve_endpoint():
    response = client.get("/api/spoilage-curve?crop=Cotton&quantity=10")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Cotton"
    assert "curve" in data
