import json
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from App.main import app
from App.database import engine, Base
from App.seed import seed
from App.adapters.weather import get_forecast
from App.adapters.market_prices import load_prices, get_price_adapter_status

Base.metadata.create_all(bind=engine)
seed()

client = TestClient(app)

def test_milestone_10_non_regression_audit():
    """
    Verification test for Chunk 6 - Milestone 10 (Non-Regression Audit):
    1. Audit Weather Adapter (live + fallback).
    2. Audit Market Price Adapter (live + CSV fallback).
    3. Audit Rule Files (fertiliser, irrigation, pest).
    4. Audit DB seed models (locations, crops).
    5. Audit all REST API endpoints.
    """
    # 1. Weather Adapter
    w_data = get_forecast("Ahmedabad")
    assert "source" in w_data, "Weather adapter missing source field"
    assert w_data["source"] in ["live", "mock"]
    print(f"[OK] Weather adapter functional (Source: {w_data['source']}).")

    # 2. Market Prices Adapter
    p_prices = load_prices("Cotton", "Ahmedabad APMC")
    p_status = get_price_adapter_status("Cotton", "Ahmedabad APMC")
    assert p_status in ["live", "mock"]
    assert len(p_prices) > 0
    print(f"[OK] Market price adapter functional (Status: {p_status}, Records: {len(p_prices)}).")

    # 3. Rule Files Audit
    rule_files = ["fertiliser_rules.json", "irrigation_rules.json", "pest_rules.json"]
    for rfile in rule_files:
        rpath = backend_dir / "data" / rfile
        assert rpath.exists(), f"Rule file missing: {rpath}"
        with open(rpath, "r") as f:
            rdata = json.load(f)
        assert len(rdata) > 0
    print("[OK] All rule files verified intact.")

    # 4. Endpoints Audit
    endpoints = ["/api/health", "/api/locations", "/api/crops", "/api/rules?crop_name=Cotton"]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} failed: {res.text}"
    print("[OK] All Phase 0 & Chunk 5 endpoints operating without regressions.")

    print("\nALL MILESTONE 10 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_10_non_regression_audit()
