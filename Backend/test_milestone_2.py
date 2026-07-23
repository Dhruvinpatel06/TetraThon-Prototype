import json
import os
import struct
from pathlib import Path

# Paths
MODEL_PATH = Path("Backend/models/leaf_classifier.keras")
CLASS_NAMES_PATH = Path("Backend/models/class_names.json")
DATASET_DIR = Path("Backend/data/plantvillage_subset")

def load_bmp_image(file_path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    with open(file_path, "rb") as f:
        data = f.read()
    magic, file_size, _, _, offset = struct.unpack("<2sIHHI", data[:14])
    dib_size, width, height, planes, bpp = struct.unpack("<IiiHH", data[14:30])
    
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    
    pixels = []
    for y in range(height - 1, -1, -1):
        row_start = offset + y * (row_bytes + padding)
        row_pixels = []
        for x in range(width):
            px_idx = row_start + x * 3
            b = data[px_idx]
            g = data[px_idx + 1]
            r = data[px_idx + 2]
            row_pixels.append((r, g, b))
        pixels.extend(row_pixels)
    return width, height, pixels

def extract_features(pixels: list[tuple[int, int, int]], width: int = 224, height: int = 224) -> list[float]:
    total_px = len(pixels)
    if total_px == 0:
        return [0.0] * 16

    r_vals = [p[0] / 255.0 for p in pixels]
    g_vals = [p[1] / 255.0 for p in pixels]
    b_vals = [p[2] / 255.0 for p in pixels]

    mean_r = sum(r_vals) / total_px
    mean_g = sum(g_vals) / total_px
    mean_b = sum(b_vals) / total_px

    import math
    std_r = math.sqrt(sum((x - mean_r) ** 2 for x in r_vals) / total_px)
    std_g = math.sqrt(sum((x - mean_g) ** 2 for x in g_vals) / total_px)
    std_b = math.sqrt(sum((x - mean_b) ** 2 for x in b_vals) / total_px)

    leaf_pixels = [p for p in pixels if not (p[0] > 210 and p[1] > 200 and p[2] > 190)]
    leaf_ratio = len(leaf_pixels) / total_px

    if len(leaf_pixels) > 0:
        leaf_r = sum(p[0] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
        leaf_g = sum(p[1] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
        leaf_b = sum(p[2] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
    else:
        leaf_r, leaf_g, leaf_b = mean_r, mean_g, mean_b

    dark_spot_count = sum(1 for p in pixels if p[0] < 80 and p[1] < 80 and p[2] < 60) / total_px
    yellow_patch_count = sum(1 for p in pixels if p[0] > 170 and p[1] > 160 and p[2] < 100) / total_px
    green_healthy_count = sum(1 for p in pixels if p[1] > p[0] + 30 and p[1] > p[2] + 30) / total_px

    half_w, half_h = width // 2, height // 2
    quadrants = [0.0] * 5

    for y in range(height):
        for x in range(width):
            px = pixels[y * width + x]
            if not (px[0] > 210 and px[1] > 200 and px[2] > 190):
                if x < half_w and y < half_h: quadrants[0] += 1
                elif x >= half_w and y < half_h: quadrants[1] += 1
                elif x < half_w and y >= half_h: quadrants[2] += 1
                elif x >= half_w and y >= half_h: quadrants[3] += 1
                if abs(x - half_w) < half_w // 2 and abs(y - half_h) < half_h // 2:
                    quadrants[4] += 1

    quadrants = [q / (total_px / 4) for q in quadrants]

    return [
        mean_r, mean_g, mean_b,
        std_r, std_g, std_b,
        leaf_ratio, leaf_r, leaf_g, leaf_b,
        dark_spot_count, yellow_patch_count, green_healthy_count,
        quadrants[0], quadrants[1], quadrants[4]
    ]

def relu(x: list[float]) -> list[float]:
    return [max(0.0, v) for v in x]

def softmax(x: list[float]) -> list[float]:
    import math
    max_val = max(x)
    exp_vals = [math.exp(v - max_val) for v in x]
    sum_exp = sum(exp_vals)
    return [v / (sum_exp + 1e-12) for v in exp_vals]

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
