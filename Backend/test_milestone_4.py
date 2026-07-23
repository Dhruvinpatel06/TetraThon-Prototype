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

# Ensure database tables and seed data exist
Base.metadata.create_all(bind=engine)
seed()

client = TestClient(app)

CLASS_NAMES_PATH = backend_dir / "models" / "class_names.json"
DATASET_DIR = backend_dir / "data" / "plantvillage_subset"

def test_milestone_4_backend_endpoint():
    """
    Verification test for Chunk 6 - Milestone 4:
    1. Verify POST /api/leaf-classify endpoint with valid image uploads for all 6 classes.
    2. Verify response JSON schema: predicted_class, confidence, is_healthy, top_predictions.
    3. Verify edge cases: invalid non-image file type returns 400, empty upload returns 400.
    4. Verify existing Phase 0 & Chunk 5 endpoints (/api/health, /api/crops, /api/locations) still work.
    """
    # 1. Test existing endpoints for non-regression
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health endpoint failed: {res.text}"
    print("[OK] GET /api/health returned 200 OK.")

    res = client.get("/api/crops")
    assert res.status_code == 200, f"Crops endpoint failed: {res.text}"
    print("[OK] GET /api/crops returned 200 OK.")

    res = client.get("/api/locations")
    assert res.status_code == 200, f"Locations endpoint failed: {res.text}"
    print("[OK] GET /api/locations returned 200 OK.")

    # 2. Test POST /api/leaf-classify with valid images across 6 classes
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    for cls_name in class_names:
        cls_dir = DATASET_DIR / cls_name
        test_file = list(cls_dir.glob("*.bmp"))[0]

        with open(test_file, "rb") as f:
            file_bytes = f.read()

        response = client.post(
            "/api/leaf-classify",
            files={"file": (test_file.name, file_bytes, "image/bmp")}
        )

        assert response.status_code == 200, f"Classification failed for {cls_name}: {response.text}"
        data = response.json()

        assert "predicted_class" in data, "Missing 'predicted_class' in response"
        assert "confidence" in data, "Missing 'confidence' in response"
        assert "is_healthy" in data, "Missing 'is_healthy' in response"
        assert "top_predictions" in data, "Missing 'top_predictions' in response"

        assert data["predicted_class"] == cls_name, f"Expected {cls_name}, got {data['predicted_class']}"
        assert data["confidence"] > 0.80, f"Low confidence ({data['confidence']}) for {cls_name}"
        assert data["is_healthy"] == ("healthy" in cls_name)
        assert len(data["top_predictions"]) <= 3

        print(f"[OK] Classified {cls_name:25s} -> {data['predicted_class']:25s} (Conf: {data['confidence']:.2%}, Healthy: {data['is_healthy']})")

    # 3. Test Edge Case: Non-image file upload
    response = client.post(
        "/api/leaf-classify",
        files={"file": ("notes.txt", b"Hello text file content", "text/plain")}
    )
    assert response.status_code == 400, f"Expected 400 for text file, got {response.status_code}"
    print("[OK] Non-image upload correctly returned HTTP 400 Bad Request.")

    # 4. Test Edge Case: Empty file upload
    response = client.post(
        "/api/leaf-classify",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400, f"Expected 400 for empty file, got {response.status_code}"
    print("[OK] Empty file upload correctly returned HTTP 400 Bad Request.")

    print("\nALL MILESTONE 4 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_4_backend_endpoint()
