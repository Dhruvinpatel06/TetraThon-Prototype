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

try:
    from ..models.ml_utils import extract_features, relu, softmax
except ImportError:
    from models.ml_utils import extract_features, relu, softmax

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def preprocess_image(image_bytes: bytes, width: int = 224, height: int = 224) -> list[float]:
    """
    Decode image bytes into RGB pixels and extract a normalized feature vector.

    Supported formats (via PIL): JPEG, PNG, WEBP, BMP, and any format PIL recognises.
    Falls back to a pure-Python 24-bit BMP parser when PIL is unavailable.
    Raises ValueError for empty, corrupt, or non-image inputs so callers can
    surface a clean HTTP 400 instead of a silently wrong prediction.
    """
    if not image_bytes:
        raise ValueError("Image data is empty.")

    pixels: list[tuple[int, int, int]] = []

    # --- Path 1: PIL (preferred, handles JPEG / PNG / WEBP / BMP / etc.) ---
    if HAS_PIL:
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((width, height))
            pixels = list(img.getdata())
        except Exception:
            pixels = []

    # --- Path 2: Pure-Python 24-bit BMP parser (PIL-absent fallback only) ---
    if not pixels:
        if image_bytes[:2] == b"BM" and len(image_bytes) >= 54:
            _, _, _, _, offset = struct.unpack("<2sIHHI", image_bytes[:14])
            _, w, h, _, bpp = struct.unpack("<IiiHH", image_bytes[14:30])
            if bpp == 24 and w > 0 and h > 0:
                row_bytes = w * 3
                padding = (4 - (row_bytes % 4)) % 4
                stride = row_bytes + padding
                for y in range(h - 1, -1, -1):
                    row_start = offset + y * stride
                    for x in range(w):
                        px_idx = row_start + x * 3
                        if px_idx + 2 < len(image_bytes):
                            b_val = image_bytes[px_idx]
                            g_val = image_bytes[px_idx + 1]
                            r_val = image_bytes[px_idx + 2]
                            pixels.append((r_val, g_val, b_val))

    # --- No valid pixels decoded: input is corrupt / unsupported ---
    if not pixels:
        raise ValueError(
            "Could not decode image. Ensure the file is a valid JPEG, PNG, BMP, or WEBP image."
        )

    return extract_features(pixels, width, height)

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
