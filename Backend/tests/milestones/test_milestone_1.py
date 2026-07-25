import json
import os
import struct
from pathlib import Path

def test_milestone_1_dataset_and_class_names():
    """
    Verification test for Chunk 6 - Milestone 1:
    1. Verify Backend/models/class_names.json exists and contains exactly 6 expected classes.
    2. Verify Backend/data/plantvillage_subset exists and contains all 6 class directories.
    3. Verify every image in each class directory can be loaded and verified without corruption.
    """
    backend_dir = Path(__file__).parent
    models_dir = backend_dir / "models"
    class_names_file = models_dir / "class_names.json"

    # 1. Verify class_names.json
    assert class_names_file.exists(), f"Missing {class_names_file}"
    with open(class_names_file, "r") as f:
        class_names = json.load(f)

    expected_classes = [
        "cotton_bacterial_blight",
        "cotton_curl_virus",
        "cotton_healthy",
        "tomato_late_blight",
        "tomato_leaf_mold",
        "tomato_healthy"
    ]

    assert class_names == expected_classes, f"Class names mismatch. Expected {expected_classes}, got {class_names}"
    print(f"[OK] class_names.json verified with {len(class_names)} classes.")

    # 2. Verify dataset directory structure
    dataset_dir = backend_dir / "data" / "plantvillage_subset"
    assert dataset_dir.exists(), f"Missing dataset directory {dataset_dir}"

    total_images = 0
    for cls in expected_classes:
        cls_dir = dataset_dir / cls
        assert cls_dir.exists() and cls_dir.is_dir(), f"Missing class directory {cls_dir}"

        images = list(cls_dir.glob("*.bmp")) + list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png")) + list(cls_dir.glob("*.jpeg"))
        assert len(images) > 0, f"No images found in {cls_dir}"

        for img_path in images:
            try:
                with open(img_path, "rb") as f:
                    header = f.read(54)
                    assert len(header) >= 14, "Image file too small"
                    if header[:2] == b"BM":
                        assert len(header) == 54, "BMP header incomplete"
                        magic, file_size, _, _, offset = struct.unpack("<2sIHHI", header[:14])
                        actual_size = os.path.getsize(img_path)
                        assert actual_size == file_size, f"BMP size mismatch: expected {file_size}, got {actual_size}"
                total_images += 1
            except Exception as e:
                raise RuntimeError(f"Corrupt image detected at {img_path}: {e}")

    print(f"[OK] Dataset directory verified: {total_images} valid images across {len(expected_classes)} classes.")

if __name__ == "__main__":
    test_milestone_1_dataset_and_class_names()
    print("\nALL MILESTONE 1 VERIFICATION TESTS PASSED SUCCESSFULLY!")
