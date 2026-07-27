# Chunk 6 — Execution Plan

## Leaf-Disease Photo Classifier

| Field | Value |
|-------|-------|
| **Owner** | Om B Patel (P2) |
| **Phase** | Phase 1 — Hackathon MVP |
| **Depends on** | Chunk 5 (Live weather + price adapters with silent fallback, deployed on Render) |
| **Deliverable** | Real leaf-disease classifier using lightweight CNN, TFLite export, `POST /leaf-classify` endpoint, wired to existing photo upload field, deployed without breaking any Phase 0 features |
| **PRD Ref** | §7.1 (FR-A5), §15.2 (MVP Scope - Leaf Classifier), §13.1 (Risks — limited accuracy) |
| **Chunk Plan Ref** | Full Phase Chunk Plan § Chunk 6 |

---

## Table of Contents

1. [Pre-Flight Audit — What Chunk 5 Left You](#1-pre-flight-audit--what-chunk-5-left-you)
2. [Dataset Preparation — PlantVillage Subset](#2-dataset-preparation--plantvillage-subset)
3. [Model Training — MobileNetV2 Transfer Learning](#3-model-training--mobilenetv2-transfer-learning)
4. [Model Export — TFLite Conversion](#4-model-export--tflite-conversion)
5. [Backend — Leaf Classify Endpoint](#5-backend--leaf-classify-endpoint)
6. [Frontend — Wire Photo Upload in AdvisoryForm](#6-frontend--wire-photo-upload-in-advisoryform)
7. [Frontend — Add Photo Upload to UnifiedScenarioForm](#7-frontend--add-photo-upload-to-unifiedscenarioform)
8. [Frontend — Leaf Classification Result Display](#8-frontend--leaf-classification-result-display)
9. [Testing — Sample Photos & Edge Cases](#9-testing--sample-photos--edge-cases)
10. [Deployment & Integration Verification](#10-deployment--integration-verification)
11. [Done Criteria Checklist](#11-done-criteria-checklist)
12. [Handoff to P3 Template](#12-handoff-to-p3-template)
13. [Ponytail Simplification Log](#13-ponytail-simplification-log)
14. [Risk Register](#14-risk-register)
15. [Milestone Summary](#15-milestone-summary)

---

## 1. Pre-Flight Audit — What Chunk 5 Left You

Before building anything in Chunk 6, verify Chunk 5 is deployed and working.

### 1.1 What Exists (Chunk 5 Deliverables)

| Component / File | Status | Description / Capability |
|------------------|--------|--------------------------|
| `Backend/App/adapters/weather.py` | ✅ Done | Live OpenWeatherMap + silent mock fallback |
| `Backend/App/adapters/market_prices.py` | ✅ Done | Live data.gov.in + silent CSV fallback |
| `Backend/App/adapters/config.py` | ✅ Done | API keys from environment variables |
| `Frontend/src/components/DataStatusIndicator.jsx` | ✅ Done | Live/mock data source badge |
| `Backend/App/routers/health.py` | ✅ Done | Returns adapter source status |

### 1.2 What Exists (Relevant Phase 0 Components)

| Component / File | Status | Description / Capability |
|------------------|--------|--------------------------|
| `Frontend/src/components/AdvisoryForm.jsx` | ✅ Done | Has a **disabled** photo upload field (lines 139-151) with "Coming Soon" label |
| `Frontend/src/components/UnifiedScenarioForm.jsx` | ✅ Done | **No photo upload field** — only advisory + post-harvest fields |
| `Frontend/src/components/AdvisoryResult.jsx` | ✅ Done | Shows 3 advisory cards; no leaf classification result section |
| `Frontend/src/api.js` | ✅ Done | Has `postAdvisory`, `postPostHarvest`; **no `postLeafClassify`** |
| `Backend/App/routers/advisory.py` | ✅ Done | Saves `photo_path=None` in FarmerSession (placeholder) |
| `Backend/requirements.txt` | ✅ Done | Includes `httpx` from Chunk 5 |

### 1.3 What You Must NOT Change

- Do NOT modify weather or price adapters (`weather.py`, `market_prices.py`, `config.py`)
- Do NOT modify decision engine logic (`advisory.py`, `spoilage.py`, `transport.py`, `decision.py`)
- Do NOT break existing API endpoints (`/health`, `/locations`, `/crops`, `/advisory`, `/post-harvest`, `/rules`)
- Do NOT remove or break the DataStatusIndicator

### 1.4 What You Need to Add in Chunk 6

| Target File | Purpose & Responsibility |
|-------------|--------------------------|
| `Backend/models/leaf_classifier.py` | **NEW:** TFLite model loading + inference wrapper |
| `Backend/models/class_names.json` | **NEW:** Mapping from class index to disease/pest name |
| `Backend/App/routers/leaf_classify.py` | **NEW:** `POST /api/leaf-classify` endpoint |
| `Backend/requirements.txt` | Add `tensorflow` or `tflite-runtime`, `Pillow`, `numpy` |
| `Frontend/src/api.js` | Add `postLeafClassify()` method |
| `Frontend/src/components/AdvisoryForm.jsx` | **UPDATE:** Enable photo upload, wire to `/api/leaf-classify` |
| `Frontend/src/components/UnifiedScenarioForm.jsx` | **UPDATE:** Add photo upload field |
| `Frontend/src/components/LeafResult.jsx` | **NEW:** Display leaf classification result card |
| `Frontend/src/components/AdvisoryResult.jsx` | **UPDATE:** Show LeafResult alongside advisories |
| `Backend/data/plantvillage_subset/` | **NEW:** Sample images for testing (not committed to git) |
| `Docs/chunk-6-execution-plan.md` | THIS DOCUMENT |

### 1.5 File Structure After Chunk 6

```
TetraThon-Prototype/
├── Backend/
│   ├── App/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   ├── adapters/
│   │   ├── engine/
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── advisory.py
│   │       ├── crops.py
│   │       ├── health.py
│   │       ├── leaf_classify.py     # NEW
│   │       ├── locations.py
│   │       ├── post_harvest.py
│   │       └── rules.py
│   ├── models/
│   │   ├── leaf_classifier.py       # NEW — TFLite inference wrapper
│   │   └── class_names.json         # NEW — class index mapping
│   ├── data/
│   │   ├── fertiliser_rules.json
│   │   ├── irrigation_rules.json
│   │   ├── mandi_prices.csv
│   │   ├── pest_rules.json
│   │   └── plantvillage_subset/     # NEW — test images (gitignored)
│   ├── requirements.txt             # + tensorflow, Pillow, numpy
│   └── Procfile
├── Frontend/
│   ├── src/
│   │   ├── api.js                   # + postLeafClassify
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── AdvisoryForm.jsx     # UPDATED — photo upload enabled
│   │       ├── AdvisoryResult.jsx   # UPDATED — shows leaf result
│   │       ├── LeafResult.jsx       # NEW
│   │       ├── ...
│   │       └── DataStatusIndicator.jsx
│   ├── ...
│   └── package.json
├── Docs/
│   ├── chunk-5-execution-plan.md
│   ├── chunk-6-execution-plan.md    # THIS DOCUMENT
│   └── ...
└── Readme.md
```

---

## 2. Dataset Preparation — PlantVillage Subset

**Dependencies:** None | **Resources:** Kaggle, ~500MB disk space

### 2.1 Dataset Source

Download the **PlantVillage dataset** from Kaggle:
- URL: https://www.kaggle.com/datasets/emmarex/plantdisease
- Use only 1–2 crops from your 4 seeded crops that have the most/clearest sample images

Recommended crops for leaf classification:

| Crop | Diseases in PlantVillage | Sample Count | Recommended? |
|------|--------------------------|-------------|--------------|
| **Cotton** | Bacterial blight, curl virus, healthy | ~2,500 | ✅ Best — clear visual symptoms |
| **Tomato** | Late blight, leaf mold, bacterial spot, healthy | ~15,000 | ✅ Best — largest set, many diseases |
| Wheat | Rust, healthy | ~1,500 | ⚠️ OK — fewer disease classes |
| Groundnut | Leaf spot, rust, healthy | ~800 | ⚠️ Small sample |

**Recommendation:** Focus on **Cotton** and **Tomato** — they have the most visually distinct disease symptoms and largest sample sizes.

### 2.2 Dataset Organization

Organize the subset as:

```
Backend/data/plantvillage_subset/
├── cotton_bacterial_blight/
│   ├── image_001.jpg
│   └── ...
├── cotton_curl_virus/
│   └── ...
├── cotton_healthy/
│   └── ...
├── tomato_late_blight/
│   └── ...
├── tomato_leaf_mold/
│   └── ...
├── tomato_healthy/
│   └── ...
```

### 2.3 Class Index Mapping (`Backend/models/class_names.json`)

```json
[
  "cotton_bacterial_blight",
  "cotton_curl_virus",
  "cotton_healthy",
  "tomato_late_blight",
  "tomato_leaf_mold",
  "tomato_healthy"
]
```

### 2.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 2.1 | Download PlantVillage from Kaggle | 15–20 min download | Dataset available locally |
| 2.2 | Create subset for Cotton + Tomato | Copy only relevant class folders | ~2,000–5,000 images |
| 2.3 | Split into train/validation | 80/20 split | `train/` and `val/` dirs |
| 2.4 | Create `class_names.json` | Ordered list matching model output | 6 class names |
| 2.5 | Verify images load correctly | `python -c "from PIL import Image; Image.open('path.jpg')"` | No corrupt images |

---

## 3. Model Training — MobileNetV2 Transfer Learning

**Dependencies:** 2 (dataset ready) | **Resources:** Python, TensorFlow/PyTorch, GPU optional

### 3.1 Approach

Use **MobileNetV2** (lightweight CNN) with transfer learning:
- Freeze base layers of pre-trained MobileNetV2
- Add a custom classification head (GlobalAveragePooling → Dense → Dropout → Dense)
- Train only the head on the PlantVillage subset

This approach:
- Needs only 100–200 training steps (not days)
- Produces a model <10MB in size
- Runs inference in <500ms even on CPU

### 3.2 Training Script (`scripts/train_classifier.py`)

```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 224
BATCH_SIZE = 32
DATASET_PATH = "Backend/data/plantvillage_subset"
CLASS_NAMES = [
    "cotton_bacterial_blight", "cotton_curl_virus", "cotton_healthy",
    "tomato_late_blight", "tomato_leaf_mold", "tomato_healthy"
]

# Data augmentation for training
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Load pre-trained MobileNetV2 (no top)
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False  # Freeze base layers

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(len(CLASS_NAMES), activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    validation_data=val_generator,
    validation_steps=val_generator.samples // BATCH_SIZE,
    epochs=10
)

# Save in both Keras and TFLite formats
model.save("Backend/models/leaf_classifier.keras")
```

### 3.3 Expected Accuracy

| Metric | Expected Value | Notes |
|--------|---------------|-------|
| Training accuracy | >90% | After 10 epochs |
| Validation accuracy | >80% | 80/20 split on subset |
| Inference time | <500ms | CPU, 224×224 input |
| Model size | <10MB | TFLite quantized |

### 3.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 3.1 | Create `scripts/train_classifier.py` | MobileNetV2 transfer learning script | File created |
| 3.2 | Install TensorFlow | `pip install tensorflow` | Import succeeds |
| 3.3 | Run training | `python scripts/train_classifier.py` | Training completes, accuracy >80% |
| 3.4 | Save Keras model | `model.save("Backend/models/leaf_classifier.keras")` | File exists |
| 3.5 | Test with sample image | Load model, predict on 1 test image | Returns class with confidence |

---

## 4. Model Export — TFLite Conversion

**Dependencies:** 3 (trained model) | **Resources:** Python, TensorFlow

### 4.1 Conversion Script

```python
import tensorflow as tf

# Load trained model
model = tf.keras.models.load_model("Backend/models/leaf_classifier.keras")

# Convert to TFLite with quantization (smaller file, slightly lower accuracy)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save TFLite model
with open("Backend/models/leaf_classifier.tflite", "wb") as f:
    f.write(tflite_model)

print(f"TFLite model saved: {len(tflite_model)} bytes")
```

### 4.2 Why TFLite

| Factor | Full Keras Model | TFLite (Quantized) |
|--------|-----------------|---------------------|
| File size | ~20MB | ~5-6MB |
| Inference speed | ~300ms | ~150ms |
| Dependency | `tensorflow` (heavy) | `tflite-runtime` (light) |
| Deployment | Needs full TF install | Works anywhere |

For a prototype, `tflite-runtime` is sufficient and avoids the heavy `tensorflow` dependency on Render.

### 4.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 4.1 | Run TFLite conversion | `python scripts/convert_to_tflite.py` | `leaf_classifier.tflite` created |
| 4.2 | Verify TFLite inference | Load tflite model, predict on 1 image | Same class as Keras model |
| 4.3 | Keep Keras model as fallback | For re-training if needed | `leaf_classifier.keras` retained |
| 4.4 | Add to `.gitignore` | `*.tflite` and `*.keras` in `.gitignore` | No large model files committed |

---

## 5. Backend — Leaf Classify Endpoint

**Dependencies:** 4 (TFLite model ready) | **Resources:** FastAPI, `tflite-runtime`

### 5.1 Inference Wrapper (`Backend/models/leaf_classifier.py`)

```python
import json
import numpy as np
from pathlib import Path
from PIL import Image

MODEL_DIR = Path(__file__).parent
TFLITE_PATH = MODEL_DIR / "leaf_classifier.tflite"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

# Lazy-load interpreter on first call
_interpreter = None
_class_names = None

def _load_model():
    global _interpreter
    if _interpreter is None:
        import tflite_runtime.interpreter as tflite
        _interpreter = tflite.Interpreter(model_path=str(TFLITE_PATH))
        _interpreter.allocate_tensors()

def _load_class_names() -> list[str]:
    global _class_names
    if _class_names is None:
        with open(CLASS_NAMES_PATH) as f:
            _class_names = json.load(f)
    return _class_names

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Resize, normalize, and add batch dimension."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)

def classify(image_bytes: bytes) -> dict:
    """Run inference, return predicted class and confidence."""
    _load_model()
    class_names = _load_class_names()
    
    input_data = preprocess_image(image_bytes)
    
    input_details = _interpreter.get_input_details()
    output_details = _interpreter.get_output_details()
    
    _interpreter.set_tensor(input_details[0]['index'], input_data)
    _interpreter.invoke()
    
    predictions = _interpreter.get_tensor(output_details[0]['index'])[0]
    predicted_idx = int(np.argmax(predictions))
    confidence = float(predictions[predicted_idx])
    
    predicted_class = class_names[predicted_idx] if predicted_idx < len(class_names) else "unknown"
    
    # Build top-3 predictions
    top_indices = np.argsort(predictions)[-3:][::-1]
    top_predictions = [
        {"class": class_names[i], "confidence": float(predictions[i])}
        for i in top_indices if i < len(class_names)
    ]
    
    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "is_healthy": "healthy" in predicted_class,
        "top_predictions": top_predictions
    }
```

### 5.2 Router (`Backend/App/routers/leaf_classify.py`)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from ...models.leaf_classifier import classify

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/leaf-classify")
async def leaf_classify(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_bytes = await file.read()
        result = classify(image_bytes)
        logger.info(f"Leaf classified: {result['predicted_class']} ({result['confidence']:.2%})")
        return result
    except Exception as e:
        logger.error(f"Leaf classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
```

### 5.3 Wire into Main App

Add to `Backend/App/main.py`:

```python
from .routers import leaf_classify
app.include_router(leaf_classify.router, prefix="/api", tags=["leaf-classify"])
```

### 5.4 Requirements Update

Add to `Backend/requirements.txt`:
```
tflite-runtime>=2.14
Pillow>=10.0
numpy>=1.24
```

### 5.5 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 5.1 | Create `Backend/models/leaf_classifier.py` | TFLite inference wrapper with preprocess | File created |
| 5.2 | Create `Backend/App/routers/leaf_classify.py` | `POST /api/leaf-classify` endpoint | Router created |
| 5.3 | Wire router into `main.py` | `app.include_router(leaf_classify.router, ...)` | App starts without errors |
| 5.4 | Add dependencies to `requirements.txt` | `tflite-runtime`, `Pillow`, `numpy` | `pip install -r` succeeds |
| 5.5 | Test with sample image | `curl -X POST -F "file=@test.jpg" http://localhost:8000/api/leaf-classify` | Returns predicted class + confidence |

---

## 6. Frontend — Wire Photo Upload in AdvisoryForm

**Dependencies:** 5 (endpoint live) | **Resources:** `AdvisoryForm.jsx`

### 6.1 Changes to `AdvisoryForm.jsx`

Replace the disabled photo upload section (lines 139-151) with a working upload:

```jsx
// Add to state:
const [leafPhoto, setLeafPhoto] = useState(null)
const [leafResult, setLeafResult] = useState(null)
const [isClassifying, setIsClassifying] = useState(false)

// Add upload handler:
const handleLeafUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  setLeafPhoto(file)
  setIsClassifying(true)
  setLeafResult(null)
  try {
    const result = await api.postLeafClassify(file)
    setLeafResult(result)
  } catch (err) {
    setLeafResult({ error: err.message })
  } finally {
    setIsClassifying(false)
  }
}

// Replace the disabled photo section with:
<div className="flex flex-col border border-dashed border-emerald-200 rounded-xl p-4 bg-emerald-50">
  <label className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
    📷 Upload Leaf Image <span className="text-xs bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded font-normal uppercase tracking-wider">AI-Enhanced</span>
  </label>
  <input
    type="file"
    accept="image/*"
    onChange={handleLeafUpload}
    disabled={isSubmitting}
    className="text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white file:cursor-pointer hover:file:bg-emerald-700"
  />
  {isClassifying && (
    <div className="flex items-center gap-2 mt-2 text-xs text-emerald-700">
      <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">...</svg>
      Analyzing leaf image...
    </div>
  )}
  {leafResult && !leafResult.error && (
    <div className="mt-2 p-2 bg-white rounded-lg border border-emerald-100">
      <p className="text-xs font-bold text-emerald-800">
        {leafResult.predicted_class.replace('_', ' ').replace('_', ' ')}
        <span className="font-normal text-slate-500 ml-1">
          ({Math.round(leafResult.confidence * 100)}% confidence)
        </span>
      </p>
      {leafResult.is_healthy ? (
        <p className="text-[10px] text-green-600 mt-0.5">✅ No disease detected</p>
      ) : (
        <p className="text-[10px] text-amber-600 mt-0.5">⚠️ Disease detected — consult local KVK for confirmation</p>
      )}
    </div>
  )}
  {leafResult?.error && (
    <p className="text-xs text-red-500 mt-1.5">Classification failed: {leafResult.error}</p>
  )}
  <p className="text-xs text-slate-400 mt-1.5">AI-assisted analysis — not a certified diagnosis.</p>
</div>
```

### 6.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 6.1 | Add `postLeafClassify` to `api.js` | POST with `multipart/form-data` | Function exists |
| 6.2 | Enable photo upload in `AdvisoryForm.jsx` | Replace disabled field with working upload | File picker opens |
| 6.3 | Add classification result display | Show predicted class + confidence inline | Result appears after upload |
| 6.4 | Add disclaimer label | "AI-assisted analysis — not a certified diagnosis" | Text visible below upload |
| 6.5 | Test full flow | Upload leaf photo → classification returned | End-to-end works |

---

## 7. Frontend — Add Photo Upload to UnifiedScenarioForm

**Dependencies:** 6 (AdvisoryForm photo upload works) | **Resources:** `UnifiedScenarioForm.jsx`

### 7.1 Changes to `UnifiedScenarioForm.jsx`

The unified form currently has no photo upload field. Add one in the form grid (after the Storage Condition field):

```jsx
// Add to state:
const [leafPhoto, setLeafPhoto] = useState(null)
const [leafResult, setLeafResult] = useState(null)
const [isClassifying, setIsClassifying] = useState(false)

// Add handleLeafUpload (same as AdvisoryForm)

// Add to form grid (last field, full width):
<div className="col-span-1 md:col-span-2 flex flex-col border border-dashed border-emerald-200 rounded-xl p-4 bg-emerald-50">
  <label className="text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
    📷 Upload Leaf Image <span className="text-xs bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded font-normal uppercase tracking-wider">Optional</span>
  </label>
  <input
    type="file"
    accept="image/*"
    onChange={handleLeafUpload}
    disabled={isSubmitting}
    className="text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white file:cursor-pointer hover:file:bg-emerald-700"
  />
  {/* Classification result display — same as AdvisoryForm */}
  {/* Disclaimer: AI-assisted analysis — not a certified diagnosis */}
</div>
```

### 7.2 Include Leaf Result in Dashboard

Pass `leafResult` through `onSubmitSuccess` so `Dashboard.jsx` can display it alongside advisories and post-harvest results.

### 7.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 7.1 | Add photo upload to `UnifiedScenarioForm.jsx` | Upload field in form grid | Field renders |
| 7.2 | Wire classification result into dashboard state | Pass `leafResult` to `onSubmitSuccess` | Result available in Dashboard |
| 7.3 | Add disclaimer label | Visible below upload field | Text shown |

---

## 8. Frontend — Leaf Classification Result Display

**Dependencies:** 6, 7 (upload works in both forms) | **Resources:** `AdvisoryResult.jsx`, `Dashboard.jsx`

### 8.1 Leaf Result Component (`LeafResult.jsx`)

Create a reusable result card for displaying classification output:

```jsx
export default function LeafResult({ result }) {
  if (!result) return null
  if (result.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4">
        <p className="text-sm font-semibold text-red-700">Leaf Analysis Failed</p>
        <p className="text-xs text-red-600 mt-1">{result.error}</p>
      </div>
    )
  }

  const isHealthy = result.is_healthy
  const statusColor = isHealthy ? 'green' : 'amber'
  const icon = isHealthy ? '✅' : '⚠️'
  const statusText = isHealthy
    ? 'No disease detected — crop appears healthy'
    : `Disease detected: ${result.predicted_class.replace(/_/g, ' ')}`

  return (
    <div className={`bg-${statusColor}-50 border border-${statusColor}-200 rounded-xl p-4`}>
      <div className="flex items-start gap-3">
        <span className="text-lg">{icon}</span>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-slate-800">Leaf Image Analysis</h4>
          <p className="text-sm text-slate-700 mt-1 font-medium">{statusText}</p>
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold bg-${statusColor}-100 text-${statusColor}-800`}>
              {Math.round(result.confidence * 100)}% confidence
            </span>
            {result.top_predictions && (
              <span className="text-[10px] text-slate-400">
                Top alternatives: {result.top_predictions.slice(1).map(p => p.class.replace(/_/g, ' ')).join(', ')}
              </span>
            )}
          </div>
          {!isHealthy && (
            <p className="text-[10px] text-slate-500 mt-2 italic">
              ⓘ AI-assisted pre-screening. Please consult your local KVK or agricultural officer for a certified diagnosis.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
```

### 8.2 Add to AdvisoryResult

Add `<LeafResult result={leafResult} />` between the advisories list and the footer buttons in `AdvisoryResult.jsx`.

### 8.3 Add to Dashboard

Add `<LeafResult result={scenarioData.leafResult} />` as a full-width section between the side-by-side advisories/recommendations and the charts.

### 8.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 8.1 | Create `LeafResult.jsx` | Reusable result card component | File created |
| 8.2 | Add to `AdvisoryResult.jsx` | Show below advisories, before footer | Result visible on advisory page |
| 8.3 | Add to `Dashboard.jsx` | Full-width section between results and charts | Result visible on dashboard |
| 8.4 | Style for responsiveness | Works on mobile (375px) | No overflow |

---

## 9. Testing — Sample Photos & Edge Cases

**Dependencies:** 5, 6, 7, 8 (all features built) | **Resources:** 8-10 test images

### 9.1 Test Image Collection

Collect 8–10 sample leaf photos:
- 2–3 healthy leaves per crop
- 2–3 diseased leaves per crop (various diseases)
- 1–2 non-leaf images (to test graceful rejection)

Source from:
- PlantVillage test subset (not used in training)
- Real photos taken with phone camera
- Online open-source agricultural image repositories

### 9.2 Test Matrix

| Test Case | Input | Expected Result |
|-----------|-------|-----------------|
| Healthy cotton leaf | `cotton_healthy` test image | "healthy" prediction, >70% confidence |
| Diseased cotton leaf | `cotton_bacterial_blight` test image | "bacterial_blight" prediction, >60% confidence |
| Healthy tomato leaf | `tomato_healthy` test image | "healthy" prediction, >70% confidence |
| Diseased tomato leaf | `tomato_late_blight` test image | "late_blight" prediction, >60% confidence |
| Non-plant image | Photo of a person/object | Returns some class with low confidence (<40%) |
| Blurry image | Out-of-focus leaf photo | Returns best guess with low confidence |
| No file uploaded | Empty POST | Returns 400 error |
| Wrong file type | Upload a `.txt` file | Returns 400 error |
| Large file (>10MB) | Upload high-res photo | Returns classification (may be slow) |

### 9.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 9.1 | Collect 8–10 test images | From PlantVillage + phone camera | Images ready in `Backend/data/plantvillage_subset/test/` |
| 9.2 | Run test matrix | Classify each image via API | All cases produce reasonable results |
| 9.3 | Test graceful degradation | If model file is missing | Returns clear error, doesn't crash app |
| 9.4 | Test frontend flow | Upload via AdvisoryForm and UnifiedScenarioForm | Result appears inline |

---

## 10. Deployment & Integration Verification

**Dependencies:** 9 (tests passed) | **Resources:** Vercel, Render

### 10.1 Deployment Considerations

| Concern | Solution |
|---------|----------|
| Model file size (5–6MB) | Acceptable for Render free tier (512MB RAM) |
| `tflite-runtime` on Render | Add to `requirements.txt` — pure Python package |
| Cold start latency | Model loads on first request (lazy load), takes ~1s |
| No GPU on Render | TFLite runs on CPU — sufficient for demo |

### 10.2 Deployment Steps

| # | Task | Command / Action | Verification |
|---|------|------------------|-------------|
| 10.1 | Add `tflite-runtime`, `Pillow`, `numpy` to `requirements.txt` | File edit | Render installs without error |
| 10.2 | Add `Backend/models/leaf_classifier.tflite` to repo | `git add` (if <100MB) | Or use LFS / download on startup |
| 10.3 | Commit all changes | `git add . && git commit -m "feat(phase1): leaf-disease classifier with TFLite"` | Clean commit |
| 10.4 | Push to GitHub | `git push origin main` | Render auto-deploys |
| 10.5 | Verify endpoint | `curl -X POST -F "file=@test.jpg" https://<render-url>/api/leaf-classify` | Returns classification |
| 10.6 | Verify frontend upload | Open Vercel URL, upload leaf photo | Classification appears |
| 10.7 | Verify Phase 0 features still work | Advisory, post-harvest, dashboard, charts | No regressions |
| 10.8 | Verify Chunk 5 features still work | Live weather, live prices, data status indicator | All functional |

### 10.3 Alternative: Download Model on Startup

If the TFLite model is too large for git, download it at startup:

```python
# In leaf_classifier.py
import requests
MODEL_URL = os.getenv("TFLITE_MODEL_URL", "")
if not TFLITE_PATH.exists() and MODEL_URL:
    resp = requests.get(MODEL_URL)
    TFLITE_PATH.write_bytes(resp.content)
```

---

## 11. Done Criteria Checklist

- [ ] PlantVillage subset downloaded and organized for Cotton + Tomato
- [ ] Class names defined in `Backend/models/class_names.json`
- [ ] MobileNetV2 transfer learning training script created
- [ ] Model trained with >80% validation accuracy
- [ ] Model exported to TFLite format (<10MB)
- [ ] `Backend/models/leaf_classifier.py` inference wrapper created with lazy loading
- [ ] `POST /api/leaf-classify` endpoint created accepting `multipart/form-data`
- [ ] Endpoint validates file type (must be image)
- [ ] Router wired into `main.py`
- [ ] `tflite-runtime`, `Pillow`, `numpy` in `requirements.txt`
- [ ] `postLeafClassify()` added to `Frontend/src/api.js`
- [ ] `AdvisoryForm.jsx` photo upload enabled and wired to endpoint
- [ ] `UnifiedScenarioForm.jsx` photo upload field added
- [ ] `LeafResult.jsx` component created with healthy/diseased status display
- [ ] `AdvisoryResult.jsx` shows leaf classification result
- [ ] `Dashboard.jsx` shows leaf classification result
- [ ] Disclaimer "AI-assisted, not a certified diagnosis" visible on all classification results
- [ ] 8–10 test images collected and tested
- [ ] All test cases pass (healthy, diseased, non-leaf, no file, wrong type)
- [ ] Deployed on Render — classification works end-to-end
- [ ] Phase 0 features (advisory, post-harvest, dashboard, charts) still work
- [ ] Chunk 5 features (live weather, live prices, data status) still work

---

## 12. Handoff to P3 Template

Create `Docs/handoff-to-p3-phase1.md` to guide Person 3 (Mithil) when starting Chunk 7 (Real Price Alert — SMS/WhatsApp Simulation):

```markdown
# Handoff to Person 3 (Mithil) — Chunk 6 Completion & Chunk 7 Kickoff

Chunk 6 (Leaf-Disease Photo Classifier) is 100% complete!

## Key Deliverables Added in Chunk 6:
- **TFLite Leaf Classifier:** MobileNetV2 trained on Cotton + Tomato diseases, deployed as lightweight TFLite model.
- **POST /api/leaf-classify:** Endpoint accepting image upload → returns predicted disease + confidence + top-3 alternatives.
- **AdvisoryForm Photo Upload:** Previously disabled "Coming Soon" field is now live and working.
- **UnifiedScenarioForm Photo Upload:** Leaf image upload added for dashboard scenarios.
- **LeafResult Component:** Reusable result card showing healthy/diseased status with disclaimer.

## Starting Point for Chunk 7 (Real Price Alert — SMS/WhatsApp Simulation):
1. `Backend/`: Create new `POST /api/price-alert` endpoint with threshold storage.
2. `Backend/requirements.txt`: Add `twilio` for Twilio Sandbox integration.
3. `Frontend/src/components/`: Create price-alert UI (crop, market, target price inputs).
4. `Frontend/src/api.js`: Add `postPriceAlert()` and `checkAlerts()` methods.

## Key Files to Know:
- `Backend/App/routers/leaf_classify.py` — Leaf classifier endpoint (DO NOT MODIFY)
- `Backend/models/leaf_classifier.py` — TFLite inference wrapper (DO NOT MODIFY)
- `Frontend/src/components/LeafResult.jsx` — Classification result display (can extend if needed)

All existing UI components, DB models, rule files, and live data adapters remain 100% intact!
```

---

## 13. Ponytail Simplification Log

| Pragmatic Choice / Shortcut | Skipped Mechanism | Reason & Future Resolution | File Location |
|-----------------------------|-------------------|----------------------------|---------------|
| TFLite runtime | Full TensorFlow/Keras serving | `tflite-runtime` is 5% the size, no GPU dependency; swap for TF Serving in Phase 3 | `Backend/models/leaf_classifier.py` |
| MobileNetV2 (pre-trained) | Training from scratch | Transfer learning needs 10x less data and 100x less training time; scratches the demo | `scripts/train_classifier.py` |
| Only 2 crops classified | All 4 crops | Cotton + Tomato have best PlantVillage coverage; extend to Wheat/Groundnut in Phase 2 | `Backend/models/class_names.json` |
| Lazy model loading | Pre-load on startup | First request is ~1s slower; acceptable for demo, pre-load in Phase 2 | `Backend/models/leaf_classifier.py` |
| Client-side upload + inline result | Dedicated "Leaf Scanner" page | Reusing existing form flow avoids new UI; standalone scanner page in Phase 2 | `Frontend/src/components/AdvisoryForm.jsx` |
| No training pipeline | Airflow/Prefect scheduled retraining | Model trained once; retraining pipeline added when pilot collects real field data | `scripts/train_classifier.py` |
| Model files gitignored | DVC/Model registry | TFLite file is <10MB, committed directly; model registry in Phase 3 | `.gitignore` |
| Top-3 predictions returned | Grad-CAM heatmap visualization | Heatmap adds UX complexity without evaluator benefit; add in Phase 2 | `Backend/App/routers/leaf_classify.py` |

---

## 14. Risk Register

| Risk Scenario | Likelihood | Impact | Applied Mitigation Strategy |
|---------------|------------|--------|-----------------------------|
| Low validation accuracy (<60%) | Medium | High | Increase epochs, add data augmentation, try different base model (EfficientNet) |
| TFLite model too large for Render | Low | Medium | Download model from URL at startup instead of including in repo |
| `tflite-runtime` fails on Render Python version | Low | High | Pin Python 3.11 on Render; fall back to `tensorflow` (heavier but works) |
| Farmer uploads non-leaf image | Medium | Low | Model returns low confidence — clearly show confidence % so user understands uncertainty |
| Demo evaluator mistakes AI for certified diagnosis | Medium | Medium | Show prominent disclaimer on every classification result |
| Photo upload fails on slow mobile connection | Low | Low | Classification is optional — farmer can still get advisories without photo |
| MobileNetV2 license restriction (Apache 2.0) | Low | Low | Apache 2.0 allows commercial use; no issue for hackathon |
| PlantVillage dataset license | Low | Low | CC-BY 4.0 — attribution in README sufficient |

---

## 15. Milestone Summary

| Milestone | Verification Gate |
|-----------|-------------------|
| **M1: Dataset Prepared** | PlantVillage subset for Cotton + Tomato organized in class folders |
| **M2: Model Trained** | >80% validation accuracy after transfer learning |
| **M3: TFLite Model Exported** | `<10MB` TFLite file with quantized weights |
| **M4: Backend Endpoint Working** | `POST /api/leaf-classify` returns predicted class + confidence |
| **M5: AdvisoryForm Upload Enabled** | Photo upload field submits and shows result inline |
| **M6: UnifiedScenarioForm Upload Added** | Photo upload field in dashboard form |
| **M7: LeafResult Component Renders** | Card shows healthy/diseased status with disclaimer |
| **M8: All Test Cases Pass** | 8–10 test images classified correctly |
| **M9: Deployed & Verified** | Endpoint works on Render, frontend works on Vercel |
| **M10: No Regressions** | All Phase 0 + Chunk 5 features still functional |

---

*— End of Document —*
