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

Base.metadata.create_all(bind=engine)
seed()

client = TestClient(app)

def test_milestone_9_e2e_integration():
    """
    Verification test for Chunk 6 - Milestone 9 (Local E2E Integration):
    Verify full end-to-end user workflow:
    1. Query locations & crops.
    2. Upload leaf photo to /api/leaf-classify.
    3. Generate precision crop advisory with /api/advisory.
    4. Generate post-harvest financial plan with /api/post-harvest.
    """
    # 1. Query endpoints
    loc_res = client.get("/api/locations")
    assert loc_res.status_code == 200
    locations = loc_res.json()
    assert len(locations) >= 5

    crop_res = client.get("/api/crops")
    assert crop_res.status_code == 200
    crops = crop_res.json()
    assert len(crops) >= 4

    # 2. Upload leaf photo
    test_file = backend_dir / "data" / "plantvillage_subset" / "test" / "test_cotton_bacterial_blight.bmp"
    with open(test_file, "rb") as f:
        leaf_res = client.post("/api/leaf-classify", files={"file": (test_file.name, f.read(), "image/bmp")})
    assert leaf_res.status_code == 200
    leaf_data = leaf_res.json()
    assert leaf_data["predicted_class"] == "cotton_bacterial_blight"

    # 3. Post advisory
    adv_res = client.post("/api/advisory", json={
        "location_name": "Ahmedabad",
        "crop_name": "Cotton",
        "sowing_date": "2026-06-01",
        "weather_observation": "hot_and_dry"
    })
    assert adv_res.status_code == 200
    adv_data = adv_res.json()
    assert len(adv_data["advisories"]) == 3

    # 4. Post post-harvest
    ph_res = client.post("/api/post-harvest", json={
        "crop_name": "Cotton",
        "quantity_quintals": 15.0,
        "storage_condition": "warehouse",
        "location_name": "Ahmedabad"
    })
    assert ph_res.status_code == 200
    ph_data = ph_res.json()
    assert "recommendation" in ph_data
    assert "expected_return" in ph_data

    print("[OK] E2E Integration: Location, Crop, Leaf Classification, Advisory, and Post-Harvest flows execute seamlessly.")
    print("\nALL MILESTONE 9 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_9_e2e_integration()
