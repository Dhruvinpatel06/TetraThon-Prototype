# Chunk 2 — Execution Plan

## Module A — Precision Crop Advisory Engine

| Field | Value |
|-------|-------|
| **Owner** | Om |
| **Timing** | Day 2–3 (~16 hr net over 2 days) |
| **Phase** | Phase 0 — Pre-Screening Prototype |
| **Depends on** | Chunk 1 (repo scaffold, seed data, rule JSON files, deployed skeleton) |
| **Deliverable** | Live, deployed Module A — farmer fills a form → 3 ranked advisories with confidence + plain language |
| **PRD Ref** | §7.1 (FR-A1–A7), §11.1 (Advisory Flow), §15.2 (MVP Scope), §15.4 (Day 3–5) |
| **Chunk Plan Ref** | Full Phase Chunk Plan § Chunk 2 |

---

## Table of Contents

1. [Pre-Flight Audit — What Chunk 1 Left You](#1-pre-flight-audit--what-chunk-1-left-you)
2. [Backend — Advisory Engine & Weather Adapter](#2-backend--advisory-engine--weather-adapter)
3. [Backend — POST /advisory Endpoint](#3-backend--post-advisory-endpoint)
4. [Backend — GET /api/rules Endpoint](#4-backend--get-apirules-endpoint)
5. [Frontend — Advisory Intake Form](#5-frontend--advisory-intake-form)
6. [Frontend — Advisory Results Display](#6-frontend--advisory-results-display)
7. [Frontend — Navigation & Integration](#7-frontend--navigation--integration)
8. [Edge Case Handling & 20-Combination Test](#8-edge-case-handling--20-combination-test)
9. [Deploy & Smoke Test](#9-deploy--smoke-test)
10. [Done Criteria Checklist](#10-done-criteria-checklist)
11. [Handoff to P3 Template](#11-handoff-to-p3-template)
12. [Ponytail Simplification Log](#12-ponytail-simplification-log)
13. [Resource Summary](#13-resource-summary)
14. [Risk Register](#14-risk-register)
15. [Milestone Summary](#15-milestone-summary)

---

## 1. Pre-Flight Audit — What Chunk 1 Left You

Before building anything, read the current state to avoid double-work.

### 1.1 What Exists (Chunk 1 Deliverables)

| File | Status | Notes |
|------|--------|-------|
| `Backend/App/main.py` | ✅ Done | FastAPI app, 3 endpoints (`/health`, `/locations`, `/crops`), CORS wide open |
| `Backend/App/database.py` | ✅ Done | SQLAlchemy engine + session, SQLite |
| `Backend/App/models.py` | ✅ Done | `Location`, `Crop`, `FarmerSession` ORM models |
| `Backend/App/schemas.py` | ✅ Done | `LocationOut`, `CropOut` — read-only Pydantic schemas |
| `Backend/App/seed.py` | ✅ Done | 5 Gujarat locations, 4 crops (Cotton, Wheat, Groundnut, Tomato) |
| `Backend/Rules/irrigation_rules.json` | ✅ Done | 4 crops × 4 stages, interval-based |
| `Backend/Rules/fertiliser_rules.json` | ✅ Done | 4 crops × 4 stages, N-P-K values |
| `Backend/Rules/pest_windows.json` | ✅ Done | 4 crops × 4 stages, pest/disease risks |
| `Frontend/` | ✅ Done | React + Vite + Tailwind, fetches health/locations/crops |
| `README.md` | ✅ Done | Completed in Chuck 2 |
| Deployment | ❌ Not done | No Vercel/Render deployment yet |

### 1.2 What You Must NOT Change

- Location & Crop seed data (5 Gujarat locations, 4 crops)
- Rule JSON schema format (your engine reads these files)
- `GET /health`, `GET /locations`, `GET /crops` endpoints
- Frontend `api.js` wrapper (you will _add_ to it, not change existing methods)

### 1.3 What You Need to Add

- `Backend/App/adapters/weather.py` — mocked 7-day forecast per location
- `Backend/App/engine/advisory.py` — rule-based ranking + confidence + plain-language
- `Backend/App/routers/advisory.py` — `POST /advisory` endpoint
- `Backend/App/routers/rules.py` — `GET /api/rules?crop_id=X` (missing from Chunk 1)
- `Backend/App/schemas.py` additions — input/output Pydantic models for advisory
- `Frontend/src/components/AdvisoryForm.jsx` — intake form
- `Frontend/src/components/AdvisoryResult.jsx` — results display
- `Frontend/src/App.jsx` updates — view routing between form/results

### 1.4 File Structure After Chunk 2

```
Backend/
├── App/
│   ├── __init__.py
│   ├── main.py                  # + include advisory + rules routers
│   ├── database.py              # unchanged
│   ├── models.py                # unchanged
│   ├── schemas.py               # + AdvisoryInput, AdvisoryOutput, RuleOut
│   ├── seed.py                  # unchanged
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── weather.py           # NEW — mocked 7-day forecast
│   ├── engine/
│   │   ├── __init__.py
│   │   └── advisory.py          # NEW — ranking, scoring, templates
│   └── routers/
│       ├── __init__.py
│       ├── advisory.py          # NEW — POST /advisory
│       └── rules.py             # NEW — GET /api/rules
├── Rules/
│   ├── irrigation_rules.json    # unchanged
│   ├── fertiliser_rules.json    # unchanged
│   └── pest_windows.json        # unchanged
├── main.py                      # unchanged (entry point)
├── requirements.txt             # unchanged
├── Procfile                     # unchanged
└── .gitignore                   # unchanged

Frontend/
├── src/
│   ├── api.js                   # + postAdvisory(), getRules()
│   ├── App.jsx                  # + view state: form vs results
│   ├── App.css                  # unchanged
│   ├── main.jsx                 # unchanged
│   ├── index.css                # unchanged
│   └── components/
│       ├── AdvisoryForm.jsx     # NEW
│       └── AdvisoryResult.jsx   # NEW
├── index.html                   # unchanged
├── vite.config.js               # unchanged
├── package.json                 # unchanged
├── postcss.config.js            # unchanged
└── tailwind.config.js           # unchanged
```

---

## 2. Backend — Advisory Engine & Weather Adapter

**Timeline:** 3 hr | **Dependencies:** Chunk 1 rule JSON files | **PRD:** FR-A2, FR-A3, FR-A4

### 2.1 Mocked Weather Adapter (`Backend/App/adapters/weather.py`)

Create a module that returns a deterministic 7-day forecast for any seeded location.

| Field | Logic |
|-------|-------|
| Temperature | Varies by location (Gujarat = hot, 28–42°C range) |
| Rainfall chance | Random-percent seeded per location (deterministic, not random) |
| Humidity | 40–80% range based on location |
| Wind speed | 5–20 km/h range |

**Schema** — each `get_forecast(location_name)` call returns:

```python
{
  "location": "Anand",
  "forecast": [
    {"day": 1, "date": "2026-07-20", "temp_high": 38, "temp_low": 27, "rain_chance": 10, "humidity": 55, "wind_kph": 12},
    # ... 7 days
  ]
}
```

**Implementation notes:**
- Return `None` or raise a clear exception if location unknown (caller handles fallback)
- Keep forecast static per location — no randomness, so tests are deterministic
- File is small (~50 lines)

### 2.2 Advisory Ranking Engine (`Backend/App/engine/advisory.py`)

This is the core logic. It takes farmer inputs and returns 3 ranked advisories.

**Input:**
```python
advisory_request = {
    "location_name": "Anand",
    "crop_name": "Cotton",
    "sowing_date": "2026-06-15",
    "weather_observation": "hot_and_dry",  # optional
    "photo_uploaded": False                # optional, for future
}
```

**Logic flow:**

| Step | What it does |
|------|-------------|
| 1. Load rule files | Read the 3 JSON files from `Backend/Rules/` |
| 2. Calculate current stage | From sowing_date → days_since_sowing → find stage in rule table matching `day_range` |
| 3. Get weather context | Call `weather.get_forecast(location_name)` → merge into advisory input |
| 4. Score irrigation advisory | Based on current stage's `interval_days`, `skip_if_rain_expected`, and 7-day rain forecast |
| 5. Score fertiliser advisory | Based on current stage's N-P-K needs, return what to apply |
| 6. Score pest advisory | Based on current stage's pest/disease risk + weather observation modifier |
| 7. Rank 3 advisories | Always return 1 irrigation + 1 fertiliser + 1 pest advisory in fixed order |
| 8. Compute confidence | Per advisory: High/Medium/Low based on data completeness |

**Confidence scoring rules:**

| Condition | Irrigation Confidence | Fertiliser Confidence | Pest Confidence |
|-----------|----------------------|----------------------|-----------------|
| All data present, stage matched exactly | High | High | High |
| Weather observation missing | Medium | High | Medium |
| Stage matched but rule is generic | High | Medium | Medium |
| Sowing date very old (>crop duration) | Low | Low | Low |
| Location not in weather adapter | Low (no forecast) | High (no weather needed) | Medium |

**Plain-language templates:**

```python
TEMPLATES = {
    "irrigation": "Your {crop} is in the {stage} stage. Apply {water_cm}cm of water every {freq} day(s). {rain_advice}",
    "fertiliser": "Your {crop} is in the {stage} stage. Apply {n_kg}kg Nitrogen, {p_kg}kg Phosphorus, {k_kg}kg Potassium per acre.",
    "pest": "Your {crop} is in the {stage} stage. Watch for {pest_name} (Risk: {risk}). {observation_advice}"
}
```

**Output schema (per advisory):**
```python
{
    "type": "irrigation",  # or "fertiliser" or "pest"
    "title": "Irrigation Advisory",
    "confidence": "High",
    "plain_text": "Your Cotton is in the Flowering stage. Apply 10.0cm of water every 5 day(s). Rain expected on 2 of the next 7 days — reduce watering accordingly.",
    "details": {
        "stage": "Flowering",
        "day_range": [46, 75],
        # type-specific fields
    }
}
```

### 2.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 2.1 | Create `Backend/App/adapters/__init__.py` | Empty package marker | |
| 2.2 | Create `Backend/App/adapters/weather.py` | `get_forecast(location: str) → dict` with 5 deterministic forecasts | `python -c "from App.adapters.weather import get_forecast; print(get_forecast('Anand'))"` returns data |
| 2.3 | Create `Backend/App/engine/__init__.py` | Empty package marker | |
| 2.4 | Create `Backend/App/engine/advisory.py` | `generate_advisories(location, crop, sowing_date, weather_obs) → list[dict]` | Unit test with known input — returns 3 advisories |
| 2.5 | Verify all 4 crops × 5 locations | Engine produces valid output for all 20 combos | No crashes, all 3 advisories present per combo |
| 2.6 | Verify edge cases | Future sowing date, very old sowing date, unknown location | Graceful degradation (confidence=Low, not crash) |

---

## 3. Backend — POST /advisory Endpoint

**Timeline:** 1 hr | **Dependencies:** 2 (engine + adapter exist) | **PRD:** FR-A1, FR-A6, FR-X1

### 3.1 Pydantic Schemas to Add (`Backend/App/schemas.py`)

```python
class AdvisoryInput(BaseModel):
    location_name: str
    crop_name: str
    sowing_date: str  # ISO format YYYY-MM-DD
    weather_observation: str | None = None  # "hot_and_dry", "humid", "rainy", null

class AdvisoryOutput(BaseModel):
    advisories: list[AdvisoryItem]
    session_id: int  # from FarmerSession DB record

class AdvisoryItem(BaseModel):
    type: str
    title: str
    confidence: str  # "High" | "Medium" | "Low"
    plain_text: str
```

### 3.2 Endpoint Logic

```
POST /advisory
Body: { location_name, crop_name, sowing_date, weather_observation? }

1. Look up location and crop in DB → 404 if not found
2. Call engine.generate_advisories(...)
3. Save a FarmerSession record with input + advisory count
4. Return { advisories: [...], session_id: N }
```

### 3.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 3.1 | Add `AdvisoryInput`, `AdvisoryItem`, `AdvisoryOutput` schemas to `schemas.py` | Input validation + output serialization | |
| 3.2 | Create `Backend/App/routers/__init__.py` | Empty package marker | |
| 3.3 | Create `Backend/App/routers/advisory.py` | `POST /advisory` — validates input, calls engine, saves session, returns result | |
| 3.4 | Wire router into `main.py` | `app.include_router(advisory.router)` | |
| 3.5 | Test with curl/httpx | `POST /advisory` with valid body → 200 + 3 advisories | |
| 3.6 | Test validation errors | Missing fields → 422, unknown crop → 404 | |

---

## 4. Backend — GET /api/rules Endpoint

**Timeline:** 30 min | **Dependencies:** Rule JSON files | **PRD:** FR-A3 (reference)

Chunk 1 left this endpoint unmapped. The frontend doesn't strictly need it (the engine handles rules server-side), but it's useful for debugging and was in the original plan.

### 4.1 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 4.1 | Create `Backend/App/routers/rules.py` | `GET /api/rules?crop_name=X` — returns all 3 rule tables for that crop merged into one response | |
| 4.2 | Wire into `main.py` | `app.include_router(rules.router)` | |
| 4.3 | Verify all 4 crops | Each returns irrigation + fertiliser + pest rules | |

---

## 5. Frontend — Advisory Intake Form

**Timeline:** 2 hr | **Dependencies:** Backend endpoints working | **PRD:** FR-A1, §8 (mobile-first NFR)

### 5.1 Component: `AdvisoryForm.jsx`

A mobile-responsive single-page form with:

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| Location | `<select>` dropdown | Fetched from `GET /locations` | Required |
| Crop | `<select>` dropdown | Fetched from `GET /crops` | Required |
| Sowing Date | `<input type="date">` | Native date picker | Required, must be in past |
| Weather Observation | `<select>` dropdown | Hardcoded options: "Not sure", "Hot & Dry", "Humid & Cloudy", "Light Rain", "Heavy Rain" | Optional |
| Leaf Photo (stretch) | `<input type="file">` accept="image/*" | File upload, no processing yet | Optional |
| Submit button | `<button>` | Calls `api.postAdvisory(...)` | Disabled while submitting |

**States:**
- **Loading:** Spinner while fetching location/crop dropdown data
- **Error:** Red error banner if backend unreachable
- **Form:** Ready state with all fields
- **Submitting:** Button shows spinner, all fields disabled
- **Success:** Navigate to results view
- **Error on submit:** Red error banner with message (stay on form)

### 5.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 5.1 | Create `Frontend/src/components/AdvisoryForm.jsx` | Full form component with all fields, states, validation | |
| 5.2 | Add `api.postAdvisory(data)` to `api.js` | POST to `/advisory`, returns JSON with advisories | |
| 5.3 | Add `api.getRules(cropName)` to `api.js` | GET `/api/rules?crop_name=X` | |
| 5.4 | Test form manually | Fill fields, submit, verify network request to backend | |
| 5.5 | Mobile-responsive pass | Test at 375px width — all fields usable, labels readable | |

### 5.3 Weather Observation Options

| Option Value | Display Text |
|-------------|-------------|
| `null` | Not sure (skip) |
| `hot_and_dry` | Hot & Dry |
| `humid_cloudy` | Humid & Cloudy |
| `light_rain` | Light Rain |
| `heavy_rain` | Heavy Rain |

---

## 6. Frontend — Advisory Results Display

**Timeline:** 1.5 hr | **Dependencies:** 5 (form submits successfully) | **PRD:** FR-A3, FR-A4

### 6.1 Component: `AdvisoryResult.jsx`

Shows 3 ranked advisories in a clean card layout.

**Layout (mobile-first):**

```
┌──────────────────────────┐
│  ✅ Advisories for Cotton │
│  at Anand (seeded Jun 15)│
├──────────────────────────┤
│ ┌── Advisory #1 ────────┐│
│ │ 💧 Irrigation         ││
│ │ 🟢 High Confidence    ││
│ │ "Your Cotton is..."   ││
│ │ [Show Details ▾]      ││
│ └──────────────────────┘│
│ ┌── Advisory #2 ────────┐│
│ │ 🌿 Fertiliser         ││
│ │ 🟡 Medium Confidence  ││
│ │ "Your Cotton is..."   ││
│ │ [Show Details ▾]      ││
│ └──────────────────────┘│
│ ┌── Advisory #3 ────────┐│
│ │ 🐛 Pest Alert         ││
│ │ 🔴 Low Confidence     ││
│ │ "Your Cotton is..."   ││
│ │ [Show Details ▾]      ││
│ └──────────────────────┘│
│ [← New Advisory]         │
└──────────────────────────┘
```

**Confidence badge colors:**
- High → `bg-green-100 text-green-800`
- Medium → `bg-yellow-100 text-yellow-800`
- Low → `bg-red-100 text-red-800`

**Details expand:** Tapping an advisory card expands it to show the stage name, day range, and type-specific data (water amount, N-P-K values, pest name).

**Error state:** If backend returns an error, show a red banner and a "Try Again" button that goes back to the form.

### 6.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 6.1 | Create `Frontend/src/components/AdvisoryResult.jsx` | Results display with 3 cards, confidence badges, expandable details | |
| 6.2 | Wire into `App.jsx` | Show `AdvisoryResult` after successful submission | |
| 6.3 | Test all 20 combos | Each crop/location combo produces readable output | Visual check of plain-text quality |
| 6.4 | Mobile-responsive pass | Cards stack vertically, tap targets ≥44px | |

---

## 7. Frontend — Navigation & Integration

**Timeline:** 1 hr | **Dependencies:** 5, 6 (form + results exist) | **PRD:** §8, §11.1

### 7.1 View State in `App.jsx`

Replace the current monolithic App with a simple view-state pattern (no router library needed):

```jsx
const [view, setView] = useState('home')
// 'home' → show existing health/locations/crops dashboard (from Chunk 1)
// 'form' → show AdvisoryForm
// 'results' → show AdvisoryResult with data

// Shared state between form and results
const [lastResult, setLastResult] = useState(null)
```

**Navigation:**
- Homepage has a "Get Crop Advisory" button → navigates to form
- Form submit success → navigates to results with data
- Results "New Advisory" button → navigates back to form (clears form)
- Results "Home" button → navigates back to homepage

### 7.2 Preserving Chunk 1 Functionality

The homepage must still show health check, locations, and crops as Chunk 1 delivered. The advisory flow is an additional feature, not a replacement.

### 7.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 7.1 | Refactor `App.jsx` | Add view state, conditional rendering for home/form/results | |
| 7.2 | Add navigation elements | "Get Crop Advisory" button on home, "Home" + "New Advisory" on results | |
| 7.3 | Verify Chunk 1 still works | Homepage shows health check + locations + crops as before | |

---

## 8. Edge Case Handling & 20-Combination Test

**Timeline:** 1 hr | **Dependencies:** All above | **PRD:** FR-A6 (4 crops × 5 locations)

### 8.1 Edge Cases to Handle

| Scenario | Expected Behavior |
|----------|------------------|
| Future sowing date | Engine detects days_since < 0 → confidence=Low, advisory says "sowing date is in the future" |
| Very old sowing date (>2× crop duration) | Confidence=Low, advisory says "crop likely harvested, verify sowing date" |
| Unknown location name in POST | API returns 404 with clear message |
| Unknown crop name in POST | API returns 404 with clear message |
| Empty weather_observation (null) | Engine skips weather-dependent logic, Medium confidence on irrigation/pest |
| Backend unreachable from frontend | Form shows error banner, no crash |
| Location not in weather adapter | Engine falls back to generic forecast, marks confidence Low for weather-dependent advisories |

### 8.2 20-Combination Test Matrix

Test every (crop × location) combination:

| | Anand | Vadodara | Rajkot | Ahmedabad | Surat |
|--|-------|----------|--------|-----------|-------|
| **Cotton** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Wheat** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Groundnut** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Tomato** | ✅ | ✅ | ✅ | ✅ | ✅ |

For each combo, verify:
1. HTTP 200 response
2. 3 advisories returned (irrigation, fertiliser, pest)
3. Each advisory has non-empty `plain_text`
4. Each advisory has valid confidence value (High/Medium/Low)
5. Plain text reads sensibly (no template variables left unfilled)

### 8.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 8.1 | Run 20-combo test | Script or manual POST for all combos | All return 200 with 3 advisories |
| 8.2 | Test edge cases from §8.1 | Each edge case | Correct error/fallback behavior |
| 8.3 | Fix any crashes or bad output | Iterate on engine/adapter until clean | Re-test 20 combos after fixes |

---

## 9. Deploy & Smoke Test

**Timeline:** 45 min | **Dependencies:** All above merged and tested

### 9.1 What to Deploy

| Service | Platform | What's New |
|---------|----------|------------|
| Backend | Render | + `advisory.py` router, + engine, + weather adapter, + rules router |
| Frontend | Vercel | + `AdvisoryForm.jsx`, + `AdvisoryResult.jsx`, + `api.js` additions |

### 9.2 Smoke Test Checklist

- [ ] `GET https://<backend>.onrender.com/health` → 200
- [ ] `GET /locations` → 5 locations returned
- [ ] `GET /crops` → 4 crops returned
- [ ] `GET /api/rules?crop_name=Cotton` → rules JSON for Cotton
- [ ] `POST /advisory` with valid body → 200 + 3 advisories
- [ ] `POST /advisory` with invalid body → 4xx error
- [ ] Frontend loads at Vercel URL
- [ ] Frontend health check shows "OK"
- [ ] "Get Crop Advisory" button → form loads with dropdowns populated
- [ ] Form submit → results show 3 advisories with confidence badges
- [ ] Responsive at 375px width on both form and results screens
- [ ] Chunk 1 homepage still works (health + locations + crops visible)
- [ ] Backend CORS allows Vercel domain

### 9.3 Implementation Tasks

| # | Task | Description |
|---|------|-------------|
| 9.1 | Push backend changes to GitHub → auto-deploy on Render | Verify /health |
| 9.2 | Update `VITE_API_URL` in frontend if needed | Point to Render URL |
| 9.3 | Push frontend changes → auto-deploy on Vercel | Verify frontend loads |
| 9.4 | Update CORS in backend if Vercel domain changed | |
| 9.5 | Run full smoke test on live URLs | Complete §9.2 checklist |

---

## 10. Done Criteria Checklist

- [ ] `POST /advisory` returns 3 ranked advisories (irrigation, fertiliser, pest) for all 4 crops × 5 locations
- [ ] Each advisory has a confidence tag (High/Medium/Low) with color-coded frontend badge
- [ ] Each advisory has a plain-language sentence with real numbers filled in
- [ ] Advisory form has: location dropdown, crop dropdown, date picker, weather observation dropdown, submit button
- [ ] Advisory form is mobile-responsive (tested at 375px)
- [ ] Results screen shows 3 advisory cards, expandable for details
- [ ] "New Advisory" button on results navigates back to form
- [ ] Homepage still shows Chunk 1 health check + locations + crops
- [ ] Frontend handles: loading, empty, error, and success states on both form and results
- [ ] Backend handles: missing fields (422), unknown crop/location (404), extreme dates (graceful)
- [ ] `GET /api/rules?crop_name=X` returns rule JSON for each crop
- [ ] Backend saves a `FarmerSession` record on each advisory request (FR-X1)
- [ ] Mocked weather adapter returns deterministic 7-day forecast for all 5 locations
- [ ] Deployed on Vercel + Render, full flow works end-to-end on public URLs
- [ ] No ORM changes, no state management library, no Docker added
- [ ] Leaf photo upload field exists visually but is not processed (marked as "coming soon")

---

## 11. Handoff to P3 Template

```
Built Module A — Crop Advisory Engine on top of Chunk 1.

📍 Intake form at / → "Get Crop Advisory" → dropdowns for 5 locations, 4 crops,
   date picker, weather observation selector
🌾 POST /advisory returns 3 ranked advisories (irrigation, fertiliser, pest)
   with High/Medium/Low confidence + plain-language text
📋 Engine uses rule JSON files in Backend/Rules/ — calculates growth stage
   from sowing date, looks up stage-specific rules, scores confidence
🌤 Mocked weather adapter in backend/app/adapters/weather.py
   — deterministic 7-day forecast per location
🧪 Tested across all 4 crops × 5 locations — all 20 combos return valid output
🐛 Edge cases handled: future dates, unknown crops, missing weather obs, etc.
📁 POST /advisory saves FarmerSession records (DB persistence, FR-X1)
🔗 Backend API: https://tetrathon-api.onrender.com/docs
🔗 Frontend live: https://tetrathon-krishi-drishti.vercel.app

To test Chunk 2 is good:
→ Open frontend → click "Get Crop Advisory"
→ Pick Anand + Cotton + any past date → Submit
→ See 3 advisories with colored confidence badges
→ Hit POST /advisory directly via /docs for any crop/location combo

Your work (Chunk 3) starts in:
backend/app/engine/ — add spoilage_model.py, transport_cost.py, decision_engine.py
backend/app/routers/ — add post_harvest.py
frontend/src/components/ — add PostHarvestForm.jsx, PostHarvestResult.jsx
backend/data/ — add mandi_prices.csv (synthetic price data for 5 markets)

Chunk 1's homepage still works — health check, locations list, crops list all intact.
```

---

## 12. Ponytail Simplification Log

| Shortcut | Skipped | Add When | Location |
|----------|---------|----------|----------|
| No router library | React Router | 3+ views needed (Chunk 3 adds Post-Harvest → need proper routing) | `Frontend/src/App.jsx` |
| No state management | Context/Redux/Zustand | Form state needs persistence across views | `Frontend/src/` |
| No real weather API | OpenWeatherMap integration | Phase 1 — Chunk 5 (live data swap-in) | `Backend/App/adapters/weather.py` |
| No photo processing | Leaf disease classifier | Phase 1 — Chunk 6 (stretch goal) | `Frontend/src/components/AdvisoryForm.jsx` |
| No language toggle | i18n/internationalization | Phase 2 — field agent access | `Backend/App/engine/advisory.py` |
| No test framework | pytest | Chunk 8 — Week 2 hardening | Not applicable |
| Deterministic weather | Random/realistic variance | Sufficient for demo; add variation in Phase 1 | `Backend/App/adapters/weather.py` |
| Confidence logic is rule-based | ML-based scoring | Phase 2 — when real feedback data exists | `Backend/App/engine/advisory.py` |
| Single AdvisoryItem schema per type | Separate schemas for irrigation/fertiliser/pest | When type-specific response fields diverge significantly | `Backend/App/schemas.py` |

---

## 13. Resource Summary

| Resource | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime (unchanged from Chunk 1) |
| FastAPI | 0.110+ | REST API framework (unchanged) |
| SQLAlchemy | 2.0+ | ORM (unchanged) |
| Pydantic | 2.x | Input/output validation (already in stack) |
| Node.js | 18+ | Frontend runtime (unchanged) |
| React | 18+ | UI library (unchanged) |
| Vite | 5+ | Build tool (unchanged) |
| Tailwind CSS | 3+ | Utility CSS (unchanged) |
| SQLite | 3.x | Embedded database (unchanged) |
| Vercel | — | Frontend hosting (unchanged) |
| Render | — | Backend hosting (unchanged) |
| **New: datetime** | stdlib | Date math for growth-stage calculation |
| **New: json** | stdlib | Reading rule JSON files |
| **New: pathlib** | stdlib | File path resolution for rule files |

No new external dependencies. Everything uses Python stdlib (`datetime`, `json`, `pathlib`) plus what Chunk 1 already installed.

---

## 14. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Growth-stage math off by 1 day | Medium | Low | Use inclusive day_range check (`start <= day <= end`); test all 4 crop durations |
| Plain-language template has unfilled variables | Medium | Medium | Add format-string guard: `str.format_map(defaultdict(str, ...))` or test every combo |
| FR-A6 (20 combos) reveals inconsistencies in rule JSON | Low | Medium | Fix rule data; all combo tests catch this before deploy |
| Frontend form doesn't re-fetch dropdowns after deployment | Low | Low | Dropdowns fetched on mount, not on build |
| Backend cold-start delay on Render | High | Low | Acceptable for demo; note in handoff to warm up before demo |
| Vite proxy not configured (frontend uses CORS) | Low | Low | CORS wide open in Chunk 1 — works in dev and prod |

---

## 15. Milestone Summary

| Milestone | Time | Gate |
|-----------|------|------|
| M1 — Weather adapter returns forecast for 5 locations | T+1 hr | `python -c "from App.adapters.weather import get_forecast; print(get_forecast('Anand'))"` |
| M2 — Engine returns 3 advisories for 1 crop/location combo | T+2.5 hr | Python unit test passes for Cotton/Anand |
| M3 — `POST /advisory` returns 200 on curl | T+3.5 hr | `curl -X POST ...` returns advisories |
| M4 — All 20 combos pass engine test | T+4.5 hr | Script confirms 20/20 valid |
| M5 — Advisory form renders, submits, shows results in browser | T+6 hr | Full frontend flow works locally |
| M6 — Deployed on Vercel + Render, full flow live | T+7 hr | Public URL works end-to-end |
| M7 — Handoff note written, all PRs merged | T+7.5 hr | P3 can start immediately |
