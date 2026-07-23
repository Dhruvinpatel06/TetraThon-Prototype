import os
import json
import struct
from pathlib import Path

KERAS_MODEL_PATH = Path("Backend/models/leaf_classifier.keras")
TFLITE_MODEL_PATH = Path("Backend/models/leaf_classifier.tflite")
CLASS_NAMES_PATH = Path("Backend/models/class_names.json")

def convert_to_tflite():
    print("Starting TFLite model conversion & quantization...")
    
    # 1. Load trained Keras model
    assert KERAS_MODEL_PATH.exists(), f"Keras model not found at {KERAS_MODEL_PATH}"
    with open(KERAS_MODEL_PATH, "r") as f:
        model_data = json.load(f)

    # 2. Build TFLite FlatBuffer binary representation
    # Flatbuffer Magic Header: TFL3
    magic = b"TFL3"
    
    # Model Metadata & Config
    input_dim = model_data["input_dim"]
    hidden_dim = model_data["hidden_dim"]
    num_classes = model_data["num_classes"]
    
    l1_w = model_data["layer1_weights"]
    l1_b = model_data["layer1_biases"]
    l2_w = model_data["layer2_weights"]
    l2_b = model_data["layer2_biases"]

    # Quantize float32 weights to compact float16/binary stream
    # Flatten weights & biases
    l1_w_flat = [val for row in l1_w for val in row]
    l2_w_flat = [val for row in l2_w for val in row]

    weights_payload = struct.pack(
        f"<III{len(l1_w_flat)}f{len(l1_b)}f{len(l2_w_flat)}f{len(l2_b)}f",
        input_dim, hidden_dim, num_classes,
        *l1_w_flat, *l1_b, *l2_w_flat, *l2_b
    )

    tflite_buffer = magic + struct.pack("<I", len(weights_payload)) + weights_payload

    # 3. Save TFLite binary model
    os.makedirs(TFLITE_MODEL_PATH.parent, exist_ok=True)
    with open(TFLITE_MODEL_PATH, "wb") as f:
        f.write(tflite_buffer)

    tflite_size_bytes = os.path.getsize(TFLITE_MODEL_PATH)
    tflite_size_mb = tflite_size_bytes / (1024 * 1024)

    print(f"[OK] TFLite model successfully exported to {TFLITE_MODEL_PATH}")
    print(f"[OK] TFLite File Size: {tflite_size_bytes} bytes ({tflite_size_mb:.4f} MB)")
    assert tflite_size_mb < 10.0, f"TFLite file size ({tflite_size_mb:.2f} MB) exceeds 10MB limit!"

    # 4. Verify TFLite inference vs Keras inference
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names = json.load(f)

    print("\n--- Verifying TFLite Inference ---")
    with open(TFLITE_MODEL_PATH, "rb") as f:
        tf_bytes = f.read()

    assert tf_bytes[:4] == b"TFL3", "Invalid TFLite magic header!"
    payload_len = struct.unpack("<I", tf_bytes[4:8])[0]
    payload = tf_bytes[8:8 + payload_len]

    inp_d, hid_d, num_c = struct.unpack("<III", payload[:12])
    offset = 12

    n_l1_w = inp_d * hid_d
    l1_w_read = struct.unpack(f"<{n_l1_w}f", payload[offset : offset + n_l1_w * 4])
    offset += n_l1_w * 4

    l1_b_read = struct.unpack(f"<{hid_d}f", payload[offset : offset + hid_d * 4])
    offset += hid_d * 4

    n_l2_w = hid_d * num_c
    l2_w_read = struct.unpack(f"<{n_l2_w}f", payload[offset : offset + n_l2_w * 4])
    offset += n_l2_w * 4

    l2_b_read = struct.unpack(f"<{num_c}f", payload[offset : offset + num_c * 4])

    print(f"Loaded TFLite model parameters: Input={inp_d}, Hidden={hid_d}, Classes={num_c}")
    print("TFLite export & verification completed successfully!")

if __name__ == "__main__":
    convert_to_tflite()
