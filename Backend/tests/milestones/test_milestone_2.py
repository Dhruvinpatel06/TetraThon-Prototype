import json
import os
import struct
from pathlib import Path

import sys
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

MODEL_PATH = BASE_DIR / "models" / "leaf_classifier.keras"
CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"
DATASET_DIR = BASE_DIR / "data" / "plantvillage_subset"

from models.ml_utils import load_bmp_image, extract_features, relu, softmax

def test_milestone_2_model_training():
    """
    Verification test for Chunk 6 - Milestone 2:
    1. Verify Backend/models/leaf_classifier.keras exists.
    2. Load trained model weights and architecture.
    3. Test inference across 60 sample images per class.
    4. Assert total validation/test accuracy >= 80%.
    """
    # 1. Verify model file exists
    assert MODEL_PATH.exists(), f"Model file {MODEL_PATH} not found!"
    assert os.path.getsize(MODEL_PATH) > 0, "Model file is empty!"
    print(f"[OK] Model file verified at {MODEL_PATH} ({os.path.getsize(MODEL_PATH)} bytes).")

    # 2. Load model
    with open(MODEL_PATH, "r") as f:
        model_data = json.load(f)

    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    l1_w = model_data["layer1_weights"]
    l1_b = model_data["layer1_biases"]
    l2_w = model_data["layer2_weights"]
    l2_b = model_data["layer2_biases"]

    def predict_sample(x: list[float]) -> list[float]:
        # Layer 1
        h1_raw = [l1_b[j] for j in range(len(l1_b))]
        for i in range(len(x)):
            val = x[i]
            w_row = l1_w[i]
            for j in range(len(h1_raw)):
                h1_raw[j] += val * w_row[j]
        h1 = relu(h1_raw)

        # Layer 2
        out_raw = [l2_b[j] for j in range(len(l2_b))]
        for i in range(len(h1)):
            val = h1[i]
            w_row = l2_w[i]
            for j in range(len(out_raw)):
                out_raw[j] += val * w_row[j]
        return softmax(out_raw)

    # 3. Test accuracy across dataset
    total_samples = 0
    correct_predictions = 0

    for cls_idx, cls_name in enumerate(class_names):
        cls_dir = DATASET_DIR / cls_name
        assert cls_dir.exists(), f"Missing directory: {cls_dir}"
        
        img_files = list(cls_dir.glob("*.bmp")) + list(cls_dir.glob("*.jpg"))
        for img_path in img_files:
            _, _, pixels = load_bmp_image(img_path)
            feats = extract_features(pixels)
            probs = predict_sample(feats)
            
            pred_idx = probs.index(max(probs))
            if pred_idx == cls_idx:
                correct_predictions += 1
            total_samples += 1

    accuracy = correct_predictions / total_samples
    print(f"[OK] Tested model on {total_samples} samples across 6 classes.")
    print(f"[OK] Measured Test Accuracy: {accuracy:.2%}")

    assert accuracy >= 0.80, f"Accuracy ({accuracy:.2%}) is lower than required 80% threshold!"
    print("\nALL MILESTONE 2 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_2_model_training()
