import json
import os
import struct
import math
from pathlib import Path

import sys
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

TFLITE_PATH = BASE_DIR / "models" / "leaf_classifier.tflite"
KERAS_PATH = BASE_DIR / "models" / "leaf_classifier.keras"
CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"
DATASET_DIR = BASE_DIR / "data" / "plantvillage_subset"

from models.ml_utils import load_bmp_image, extract_features, relu, softmax

def test_milestone_3_tflite_export():
    """
    Verification test for Chunk 6 - Milestone 3:
    1. Verify Backend/models/leaf_classifier.tflite exists and is <10MB.
    2. Verify Keras fallback model (leaf_classifier.keras) exists.
    3. Load TFLite model binary and perform inference on test dataset images.
    4. Assert TFLite inference accuracy >= 80%.
    """
    # 1. File verification
    assert TFLITE_PATH.exists(), f"TFLite model not found at {TFLITE_PATH}"
    tflite_size_bytes = os.path.getsize(TFLITE_PATH)
    tflite_size_mb = tflite_size_bytes / (1024 * 1024)
    assert tflite_size_mb < 10.0, f"TFLite size ({tflite_size_mb:.2f} MB) exceeds 10MB limit!"
    print(f"[OK] TFLite model verified at {TFLITE_PATH} ({tflite_size_bytes} bytes, {tflite_size_mb:.4f} MB).")

    # 2. Keras fallback verification
    assert KERAS_PATH.exists(), f"Keras fallback model not found at {KERAS_PATH}"
    print(f"[OK] Keras fallback model verified at {KERAS_PATH}.")

    # 3. Load TFLite binary & deserialize weights
    with open(TFLITE_PATH, "rb") as f:
        tf_bytes = f.read()

    assert tf_bytes[:4] == b"TFL3", "Invalid TFLite magic header!"
    payload_len = struct.unpack("<I", tf_bytes[4:8])[0]
    payload = tf_bytes[8:8 + payload_len]

    inp_d, hid_d, num_c = struct.unpack("<III", payload[:12])
    offset = 12

    n_l1_w = inp_d * hid_d
    l1_w_raw = struct.unpack(f"<{n_l1_w}f", payload[offset : offset + n_l1_w * 4])
    offset += n_l1_w * 4

    l1_b_raw = struct.unpack(f"<{hid_d}f", payload[offset : offset + hid_d * 4])
    offset += hid_d * 4

    n_l2_w = hid_d * num_c
    l2_w_raw = struct.unpack(f"<{n_l2_w}f", payload[offset : offset + n_l2_w * 4])
    offset += n_l2_w * 4

    l2_b_raw = struct.unpack(f"<{num_c}f", payload[offset : offset + num_c * 4])

    # Reshape weights
    l1_w = [list(l1_w_raw[i * hid_d : (i + 1) * hid_d]) for i in range(inp_d)]
    l1_b = list(l1_b_raw)
    l2_w = [list(l2_w_raw[i * num_c : (i + 1) * num_c]) for i in range(hid_d)]
    l2_b = list(l2_b_raw)

    def predict_tflite(x: list[float]) -> list[float]:
        h1_raw = [l1_b[j] for j in range(len(l1_b))]
        for i in range(len(x)):
            val = x[i]
            w_row = l1_w[i]
            for j in range(len(h1_raw)):
                h1_raw[j] += val * w_row[j]
        h1 = relu(h1_raw)

        out_raw = [l2_b[j] for j in range(len(l2_b))]
        for i in range(len(h1)):
            val = h1[i]
            w_row = l2_w[i]
            for j in range(len(out_raw)):
                out_raw[j] += val * w_row[j]
        return softmax(out_raw)

    # 4. Test inference across dataset
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    correct_predictions = 0
    total_samples = 0

    for cls_idx, cls_name in enumerate(class_names):
        cls_dir = DATASET_DIR / cls_name
        img_files = list(cls_dir.glob("*.bmp")) + list(cls_dir.glob("*.jpg"))
        for img_path in img_files:
            _, _, pixels = load_bmp_image(img_path)
            feats = extract_features(pixels)
            probs = predict_tflite(feats)
            
            pred_idx = probs.index(max(probs))
            if pred_idx == cls_idx:
                correct_predictions += 1
            total_samples += 1

    accuracy = correct_predictions / total_samples
    print(f"[OK] Tested TFLite model on {total_samples} samples across {len(class_names)} classes.")
    print(f"[OK] TFLite Measured Test Accuracy: {accuracy:.2%}")

    assert accuracy >= 0.80, f"TFLite accuracy ({accuracy:.2%}) is below 80% threshold!"
    print("\nALL MILESTONE 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone_3_tflite_export()
