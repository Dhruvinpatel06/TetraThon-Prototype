import sys
import os

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from App.database import Base, engine
from App.seed import seed
from App.main import app

# Initialize DB & seed data
Base.metadata.create_all(bind=engine)
seed()

client = TestClient(app)


def audit_milestone_10():
    print("=== STARTING MILESTONE 10 DEPLOYMENT & REGRESSION AUDIT ===")
    
    # 1. /api/health
    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["status"] == "OK"
    assert "adapters" in h_data
    print(f"  [OK] /api/health: {h_data}")

    # 2. /api/locations
    loc_res = client.get("/api/locations")
    assert loc_res.status_code == 200
    locs = loc_res.json()
    assert len(locs) == 5
    print(f"  [OK] /api/locations: {len(locs)} locations returned ({', '.join([l['name'] for l in locs])})")

    # 3. /api/crops
    crop_res = client.get("/api/crops")
    assert crop_res.status_code == 200
    crops = crop_res.json()
    assert len(crops) == 4
    print(f"  [OK] /api/crops: {len(crops)} crops returned ({', '.join([c['name'] for c in crops])})")

    # 4. /api/rules
    rules_res = client.get("/api/rules?crop_name=Cotton")
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert "crop_name" in rules
    assert "irrigation" in rules
    assert "fertiliser" in rules
    assert "pest" in rules
    print(f"  [OK] /api/rules: crop rules fetched for {rules['crop_name']}")

    # 5. /api/advisory
    adv_payload = {
        "location_name": "Ahmedabad",
        "crop_name": "Cotton",
        "sowing_date": "2026-06-01",
        "weather_observation": "sunny"
    }
    adv_res = client.post("/api/advisory", json=adv_payload)
    assert adv_res.status_code == 200
    adv_data = adv_res.json()
    assert len(adv_data["advisories"]) >= 3
    print(f"  [OK] /api/advisory: {len(adv_data['advisories'])} ranked advisories generated (session_id={adv_data['session_id']})")

    # 6. /api/post-harvest
    ph_payload = {
        "crop_name": "Wheat",
        "quantity_quintals": 100.0,
        "storage_condition": "warehouse",
        "location_name": "Vadodara"
    }
    ph_res = client.post("/api/post-harvest", json=ph_payload)
    assert ph_res.status_code == 200
    ph_data = ph_res.json()
    assert ph_data["recommendation"] in ["sell_now", "store", "transport"]
    print(f"  [OK] /api/post-harvest: recommendation '{ph_data['option_label']}' (INR {ph_data['expected_return']})")

    print("\n=== MILESTONE 10 AUDIT PASSED: ALL 6 ENDPOINTS FUNCTIONAL WITH ZERO REGRESSIONS! ===")


if __name__ == "__main__":
    audit_milestone_10()
