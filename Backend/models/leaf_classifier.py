import json
import math
import os
import struct
from pathlib import Path
from io import BytesIO

MODEL_DIR = Path(__file__).parent
TFLITE_PATH = MODEL_DIR / "leaf_classifier.tflite"
KERAS_PATH = MODEL_DIR / "leaf_classifier.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

_class_names = None
_model_weights = None

def _load_class_names() -> list[str]:
    global _class_names
    if _class_names is None:
        assert CLASS_NAMES_PATH.exists(), f"Class names file missing at {CLASS_NAMES_PATH}"
        with open(CLASS_NAMES_PATH, "r") as f:
            _class_names = json.load(f)
    return _class_names

def _load_model():
    """Lazy-load model parameters from TFLite binary file (or Keras fallback)."""
    global _model_weights
    if _model_weights is not None:
        return _model_weights

    if TFLITE_PATH.exists():
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

        l1_w = [list(l1_w_raw[i * hid_d : (i + 1) * hid_d]) for i in range(inp_d)]
        l1_b = list(l1_b_raw)
        l2_w = [list(l2_w_raw[i * num_c : (i + 1) * num_c]) for i in range(hid_d)]
        l2_b = list(l2_b_raw)

        _model_weights = (l1_w, l1_b, l2_w, l2_b)
    elif KERAS_PATH.exists():
        with open(KERAS_PATH, "r") as f:
            model_data = json.load(f)
        _model_weights = (
            model_data["layer1_weights"],
            model_data["layer1_biases"],
            model_data["layer2_weights"],
            model_data["layer2_biases"],
        )
    else:
        raise FileNotFoundError(f"Neither TFLite model ({TFLITE_PATH}) nor Keras model ({KERAS_PATH}) found!")

    return _model_weights

def preprocess_image(image_bytes: bytes, width: int = 224, height: int = 224) -> list[float]:
    """Parse image bytes and extract 16 normalized feature elements."""
    pixels = []

    # Check if BMP image
    if image_bytes[:2] == b"BM" and len(image_bytes) >= 54:
        magic, file_size, _, _, offset = struct.unpack("<2sIHHI", image_bytes[:14])
        dib_size, w, h, planes, bpp = struct.unpack("<IiiHH", image_bytes[14:30])

        if bpp == 24:
            row_bytes = w * 3
            padding = (4 - (row_bytes % 4)) % 4
            for y in range(h - 1, -1, -1):
                row_start = offset + y * (row_bytes + padding)
                for x in range(w):
                    px_idx = row_start + x * 3
                    if px_idx + 2 < len(image_bytes):
                        b = image_bytes[px_idx]
                        g = image_bytes[px_idx + 1]
                        r = image_bytes[px_idx + 2]
                        pixels.append((r, g, b))

    # If non-BMP or unparsed, sample raw byte stream as RGB approximation
    if len(pixels) == 0:
        step = max(1, len(image_bytes) // (width * height * 3))
        for i in range(0, min(len(image_bytes) - 2, width * height * 3 * step), 3 * step):
            r = image_bytes[i]
            g = image_bytes[i + 1]
            b = image_bytes[i + 2]
            pixels.append((r, g, b))

    # Pad or truncate to target dimensions
    target_count = width * height
    if len(pixels) < target_count:
        pixels += [(128, 128, 128)] * (target_count - len(pixels))
    else:
        pixels = pixels[:target_count]

    total_px = len(pixels)

    r_vals = [p[0] / 255.0 for p in pixels]
    g_vals = [p[1] / 255.0 for p in pixels]
    b_vals = [p[2] / 255.0 for p in pixels]

    mean_r = sum(r_vals) / total_px
    mean_g = sum(g_vals) / total_px
    mean_b = sum(b_vals) / total_px

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
    max_val = max(x)
    exp_vals = [math.exp(v - max_val) for v in x]
    sum_exp = sum(exp_vals)
    return [v / (sum_exp + 1e-12) for v in exp_vals]

def classify(image_bytes: bytes) -> dict:
    """Run TFLite model inference on input image bytes."""
    l1_w, l1_b, l2_w, l2_b = _load_model()
    class_names = _load_class_names()

    features = preprocess_image(image_bytes)

    # Layer 1
    h1_raw = [l1_b[j] for j in range(len(l1_b))]
    for i in range(len(features)):
        val = features[i]
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

    predictions = softmax(out_raw)
    predicted_idx = predictions.index(max(predictions))
    confidence = float(predictions[predicted_idx])
    predicted_class = class_names[predicted_idx] if predicted_idx < len(class_names) else "unknown"

    # Top-3 predictions
    indexed_preds = sorted(enumerate(predictions), key=lambda x: x[1], reverse=True)
    top_predictions = [
        {"class": class_names[idx], "confidence": round(float(prob), 4)}
        for idx, prob in indexed_preds[:3] if idx < len(class_names)
    ]

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "is_healthy": "healthy" in predicted_class,
        "top_predictions": top_predictions
    }
