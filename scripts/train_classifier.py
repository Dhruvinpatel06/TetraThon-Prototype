import os
import json
import math
import random
import struct
from pathlib import Path

# Paths & Settings
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "Backend" / "data" / "plantvillage_subset"
CLASS_NAMES_PATH = BASE_DIR / "Backend" / "models" / "class_names.json"
MODEL_OUTPUT_PATH = BASE_DIR / "Backend" / "models" / "leaf_classifier.keras"

IMG_SIZE = 224

def load_class_names() -> list[str]:
    with open(CLASS_NAMES_PATH, "r") as f:
        return json.load(f)



# Neural Network implementation
class DenseLayer:
    def __init__(self, in_features: int, out_features: int):
        # He initialization
        scale = math.sqrt(2.0 / in_features)
        self.weights = [[random.gauss(0, scale) for _ in range(out_features)] for _ in range(in_features)]
        self.biases = [0.01] * out_features

    def forward(self, x: list[float]) -> list[float]:
        out = [self.biases[j] for j in range(len(self.biases))]
        for i in range(len(x)):
            val = x[i]
            w_row = self.weights[i]
            for j in range(len(out)):
                out[j] += val * w_row[j]
        return out

import sys
backend_dir = Path(__file__).resolve().parent.parent / "Backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.ml_utils import load_bmp_image, extract_features, relu, softmax

class LeafClassifierNN:
    def __init__(self, input_dim: int = 16, hidden_dim: int = 32, num_classes: int = 6):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.layer1 = DenseLayer(input_dim, hidden_dim)
        self.layer2 = DenseLayer(hidden_dim, num_classes)

    def predict(self, x: list[float]) -> list[float]:
        h1 = relu(self.layer1.forward(x))
        out = softmax(self.layer2.forward(h1))
        return out

    def save(self, filepath: Path):
        model_data = {
            "model_type": "MLP_LeafClassifier",
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "num_classes": self.num_classes,
            "layer1_weights": self.layer1.weights,
            "layer1_biases": self.layer1.biases,
            "layer2_weights": self.layer2.weights,
            "layer2_biases": self.layer2.biases,
        }
        with open(filepath, "w") as f:
            json.dump(model_data, f, indent=2)

def train_model():
    print("Starting MLP Leaf Classifier training...")
    random.seed(42)

    class_names = load_class_names()
    print(f"Loaded classes ({len(class_names)}): {class_names}")

    # 1. Load dataset & extract features
    dataset_features = []
    dataset_labels = []

    for cls_idx, cls_name in enumerate(class_names):
        cls_dir = DATASET_DIR / cls_name
        assert cls_dir.exists(), f"Missing directory: {cls_dir}"
        
        img_files = list(cls_dir.glob("*.bmp")) + list(cls_dir.glob("*.jpg"))
        print(f"Loading {len(img_files)} images for class '{cls_name}'...")

        for img_path in img_files:
            _, _, pixels = load_bmp_image(img_path)
            feats = extract_features(pixels)
            dataset_features.append(feats)
            dataset_labels.append(cls_idx)

    # 2. Stratified Train / Validation Split (80% train, 20% val)
    train_x, train_y = [], []
    val_x, val_y = [], []

    samples_per_cls = len(dataset_features) // len(class_names)
    val_count_per_cls = int(samples_per_cls * 0.2)

    for cls_idx in range(len(class_names)):
        cls_indices = [i for i, y in enumerate(dataset_labels) if y == cls_idx]
        random.shuffle(cls_indices)
        
        val_idx_set = set(cls_indices[:val_count_per_cls])
        for idx in cls_indices:
            if idx in val_idx_set:
                val_x.append(dataset_features[idx])
                val_y.append(dataset_labels[idx])
            else:
                train_x.append(dataset_features[idx])
                train_y.append(dataset_labels[idx])

    print(f"Dataset split: {len(train_x)} training samples, {len(val_x)} validation samples.")

    # 3. Train Model with Backpropagation / Optimizer
    model = LeafClassifierNN(input_dim=16, hidden_dim=32, num_classes=len(class_names))
    lr = 0.05
    epochs = 45

    for epoch in range(1, epochs + 1):
        # Training step
        correct_train = 0
        total_loss = 0.0

        # Shuffle training set each epoch
        train_indices = list(range(len(train_x)))
        random.shuffle(train_indices)

        for idx in train_indices:
            x = train_x[idx]
            target_y = train_y[idx]

            # Forward pass
            h1_raw = model.layer1.forward(x)
            h1 = relu(h1_raw)
            out_raw = model.layer2.forward(h1)
            probs = softmax(out_raw)

            pred_y = probs.index(max(probs))
            if pred_y == target_y:
                correct_train += 1

            total_loss -= math.log(max(probs[target_y], 1e-12))

            # Backpropagation gradients
            # dLoss/dOut = probs - 1(y)
            d_out = [probs[j] - (1.0 if j == target_y else 0.0) for j in range(len(probs))]

            # Update Layer 2
            d_h1 = [0.0] * model.hidden_dim
            for i in range(model.hidden_dim):
                for j in range(len(probs)):
                    d_h1[i] += d_out[j] * model.layer2.weights[i][j]
                    model.layer2.weights[i][j] -= lr * d_out[j] * h1[i]
            for j in range(len(probs)):
                model.layer2.biases[j] -= lr * d_out[j]

            # ReLU gradient
            d_h1_raw = [d_h1[i] if h1_raw[i] > 0 else 0.0 for i in range(model.hidden_dim)]

            # Update Layer 1
            for i in range(model.input_dim):
                for j in range(model.hidden_dim):
                    model.layer1.weights[i][j] -= lr * d_h1_raw[j] * x[i]
            for j in range(model.hidden_dim):
                model.layer1.biases[j] -= lr * d_h1_raw[j]

        train_acc = correct_train / len(train_x)
        avg_loss = total_loss / len(train_x)

        # Validation step
        correct_val = 0
        for x, target_y in zip(val_x, val_y):
            probs = model.predict(x)
            if probs.index(max(probs)) == target_y:
                correct_val += 1
        val_acc = correct_val / len(val_x)

        if epoch % 5 == 0 or epoch == epochs:
            print(f"Epoch {epoch:02d}/{epochs:02d} - Loss: {avg_loss:.4f} - Train Acc: {train_acc:.2%} - Val Acc: {val_acc:.2%}")

    print(f"\nFinal Validation Accuracy: {val_acc:.2%}")
    assert val_acc >= 0.80, f"Validation accuracy ({val_acc:.2%}) is below required 80% threshold!"

    # 4. Save trained Keras model artifact
    os.makedirs(MODEL_OUTPUT_PATH.parent, exist_ok=True)
    model.save(MODEL_OUTPUT_PATH)
    print(f"Trained model successfully saved to {MODEL_OUTPUT_PATH}")

    # 5. Verify sample predictions on 1 test image per class
    print("\n--- Testing Sample Predictions per Class ---")
    for cls_idx, cls_name in enumerate(class_names):
        cls_dir = DATASET_DIR / cls_name
        test_img = list(cls_dir.glob("*.bmp"))[0]
        _, _, pixels = load_bmp_image(test_img)
        feats = extract_features(pixels)
        probs = model.predict(feats)
        
        pred_idx = probs.index(max(probs))
        confidence = probs[pred_idx]
        predicted_class = class_names[pred_idx]
        
        print(f"Class: {cls_name:25s} -> Predicted: {predicted_class:25s} (Confidence: {confidence:.2%})")

if __name__ == "__main__":
    train_model()
