import sys
import os

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from App.database import Base, engine
from App.seed import seed
from App.main import app
from App.adapters.weather import get_forecast

# Ensure DB tables are created and seeded for TestClient
Base.metadata.create_all(bind=engine)
seed()

client = TestClient(app)

CROPS = ["Cotton", "Wheat", "Groundnut", "Tomato"]
LOCATIONS = ["Ahmedabad", "Vadodara", "Surat", "Rajkot", "Anand"]


def test_weather_matrix_all_locations():
    print("Testing Milestone 9: Weather Matrix Across All 5 Locations...")
    for loc in LOCATIONS:
        w_res = get_forecast(loc)
        assert w_res["location"] == loc
        assert len(w_res["forecast"]) == 7
        assert w_res["source"] in ["live", "mock"]
        print(f"  [OK] Location {loc}: 7-day forecast valid (source={w_res['source']})")


def test_price_matrix_20_combinations():
    print("\nTesting Milestone 9: Price Matrix Across All 4 Crops x 5 APMC Markets (20 Combinations)...")
    from App.adapters.market_prices import load_prices, get_latest_price, get_future_price
    
    count = 0
    for crop in CROPS:
        for loc in LOCATIONS:
            market_name = f"{loc} APMC"
            prices = load_prices(crop, market_name)
            assert len(prices) > 0, f"No prices for {crop} at {market_name}"
            latest = get_latest_price(crop, market_name)
            future = get_future_price(crop, market_name, 14)
            assert latest > 0, f"Latest price 0 for {crop} at {market_name}"
            assert future > 0, f"Future price 0 for {crop} at {market_name}"
            count += 1
    print(f"  [OK] Successfully tested all {count} crop-market combinations.")


def test_e2e_advisory_endpoint():
    print("\nTesting Milestone 9: E2E POST /api/advisory Endpoint Flow...")
    payload = {
        "location_name": "Ahmedabad",
        "crop_name": "Cotton",
        "sowing_date": "2026-06-01",
        "weather_observation": "sunny"
    }
    res = client.post("/api/advisory", json=payload)
    assert res.status_code == 200, f"Advisory failed: {res.text}"
    data = res.json()
    assert "advisories" in data
    assert "session_id" in data
    assert len(data["advisories"]) >= 3
    print(f"  [OK] Advisory generated successfully: {len(data['advisories'])} advisories returned (session_id={data['session_id']}).")


def test_e2e_post_harvest_endpoint():
    print("\nTesting Milestone 9: E2E POST /api/post-harvest Endpoint Flow...")
    payload = {
        "crop_name": "Wheat",
        "quantity_quintals": 100.0,
        "storage_condition": "warehouse",
        "location_name": "Vadodara"
    }
    res = client.post("/api/post-harvest", json=payload)
    assert res.status_code == 200, f"Post-harvest failed: {res.text}"
    data = res.json()
    assert "recommendation" in data
    assert data["recommendation"] in ["sell_now", "store", "transport"]
    assert data["expected_return"] > 0
    print(f"  [OK] Post-Harvest decision generated: {data['option_label']} (Return: INR {data['expected_return']}).")


def test_e2e_all_20_scenarios_post_harvest():
    print("\nTesting Milestone 9: Full E2E Post-Harvest Decisions for 20 Combinations...")
    count = 0
    for crop in CROPS:
        for loc in LOCATIONS:
            payload = {
                "crop_name": crop,
                "quantity_quintals": 50.0,
                "storage_condition": "open",
                "location_name": loc
            }
            res = client.post("/api/post-harvest", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["expected_return"] > 0
            count += 1
    print(f"  [OK] All {count} post-harvest scenario combinations executed with HTTP 200 OK.")


def test_e2e_fallback_toggle():
    print("\nTesting Milestone 9: Full System Behavior under Fallback Mode...")
    with patch("App.adapters.config.OPENWEATHER_API_KEY", ""):
        with patch("App.adapters.config.AGMARKNET_API_KEY", ""):
            h_res = client.get("/api/health")
            assert h_res.status_code == 200
            assert h_res.json()["adapters"]["weather"] == "mock"
            assert h_res.json()["adapters"]["prices"] == "mock"
            print("  [OK] System operates seamlessly under silent fallback mode.")


if __name__ == "__main__":
    print("=== STARTING MILESTONE 9 END-TO-END VERIFICATION ===")
    test_weather_matrix_all_locations()
    test_price_matrix_20_combinations()
    test_e2e_advisory_endpoint()
    test_e2e_post_harvest_endpoint()
    test_e2e_all_20_scenarios_post_harvest()
    test_e2e_fallback_toggle()
    print("\n=== ALL MILESTONE 9 END-TO-END TESTS PASSED SUCCESSFULLY! ===")
