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
TEST_DIR = backend_dir / "data" / "plantvillage_subset" / "test"

def test_milestone_8_test_matrix_and_edge_cases():
    """
    Verification test for Chunk 6 - Milestone 8:
    1. Test matrix against 8 sample test images (healthy, diseased, non-leaf, dark/blurry).
    2. Test edge cases: empty file, non-image type.
    """
    assert TEST_DIR.exists(), f"Missing test images directory: {TEST_DIR}"

    matrix_cases = [
        ("test_cotton_healthy.bmp", "cotton_healthy"),
        ("test_cotton_bacterial_blight.bmp", "cotton_bacterial_blight"),
        ("test_cotton_curl_virus.bmp", "cotton_curl_virus"),
        ("test_tomato_healthy.bmp", "tomato_healthy"),
        ("test_tomato_late_blight.bmp", "tomato_late_blight"),
        ("test_tomato_leaf_mold.bmp", "tomato_leaf_mold"),
    ]

    for fname, expected_cls in matrix_cases:
        fpath = TEST_DIR / fname
        assert fpath.exists(), f"Missing test image {fpath}"
        with open(fpath, "rb") as f:
            file_bytes = f.read()

        res = client.post("/api/leaf-classify", files={"file": (fname, file_bytes, "image/bmp")})
        assert res.status_code == 200, f"Failed for {fname}: {res.text}"
        data = res.json()

        assert data["predicted_class"] == expected_cls, f"{fname}: Expected {expected_cls}, got {data['predicted_class']}"
        assert data["confidence"] >= 0.80, f"{fname}: Low confidence {data['confidence']}"
        print(f"[OK] Test Matrix: {fname:32s} -> {data['predicted_class']:25s} ({data['confidence']:.2%})")

    # Non-leaf image test
    fpath = TEST_DIR / "test_non_leaf.bmp"
    with open(fpath, "rb") as f:
        res = client.post("/api/leaf-classify", files={"file": ("test_non_leaf.bmp", f.read(), "image/bmp")})
    assert res.status_code == 200, "Non-leaf image classification crashed!"
    print(f"[OK] Non-leaf abstract image processed gracefully without crash -> {res.json()['predicted_class']}")

    # Dark blurry image test
    fpath = TEST_DIR / "test_dark_blurry.bmp"
    with open(fpath, "rb") as f:
        res = client.post("/api/leaf-classify", files={"file": ("test_dark_blurry.bmp", f.read(), "image/bmp")})
    assert res.status_code == 200, "Dark blurry image classification crashed!"
    print(f"[OK] Dark blurry image processed gracefully without crash -> {res.json()['predicted_class']}")

    # Empty file
    res = client.post("/api/leaf-classify", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert res.status_code == 400, "Empty file should return 400"
    print("[OK] Empty file upload returns 400 Bad Request.")

    # Wrong file type
    res = client.post("/api/leaf-classify", files={"file": ("document.pdf", b"%PDF-1.4", "application/pdf")})
    assert res.status_code == 400, "PDF file should return 400"
    print("[OK] Wrong file type returns 400 Bad Request.")

    print("\nALL MILESTONE 8 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_8_test_matrix_and_edge_cases()
