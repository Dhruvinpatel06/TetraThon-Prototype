# Chunk 3 — Execution Plan

## Module B — Post-Harvest Loss Planner

| Field | Value |
|-------|-------|
| **Owner** | Saumya |
| **Timing** | Day 4–5 (~16 hr net over 2 days) |
| **Phase** | Phase 0 — Pre-Screening Prototype |
| **Depends on** | Chunk 2 (advisory engine, weather adapter, deployed skeleton) |
| **Deliverable** | Live Module B — farmer enters harvest details → Sell / Store / Transport recommendation with expected-return number |

---

## Table of Contents

1. [Pre-Flight Audit — What Chunk 2 Left You](#1-pre-flight-audit--what-chunk-2-left-you)
2. [Backend — Synthetic Mandi Price Data](#2-backend--synthetic-mandi-price-data)
3. [Backend — Spoilage Model](#3-backend--spoilage-model)
4. [Backend — Transport Cost Model](#4-backend--transport-cost-model)
5. [Backend — Decision Engine](#5-backend--decision-engine)
6. [Backend — POST /post-harvest Endpoint](#6-backend--post-post-harvest-endpoint)
7. [Frontend — Post-Harvest Intake Form](#7-frontend--post-harvest-intake-form)
8. [Frontend — Post-Harvest Results Display](#8-frontend--post-harvest-results-display)
9. [Frontend — Navigation & Integration](#9-frontend--navigation--integration)
10. [Edge Case Handling & Combination Test](#10-edge-case-handling--combination-test)
11. [Deploy & Smoke Test](#11-deploy--smoke-test)
12. [Done Criteria Checklist](#12-done-criteria-checklist)
13. [Handoff to P4 Template](#13-handoff-to-p4-template)
14. [Ponytail Simplification Log](#14-ponytail-simplification-log)
15. [Resource Summary](#15-resource-summary)
16. [Risk Register](#16-risk-register)
17. [Milestone Summary](#17-milestone-summary)

---

## 1. Pre-Flight Audit — What Chunk 2 Left You

### 1.1 What Exists (Chunk 2 Deliverables)

| File | Status | Notes |
|------|--------|-------|
| `Backend/App/main.py` | ✅ Done | 5 routers wired (advisory, rules, health, locations, crops), CORS wide open |
| `Backend/App/models.py` | ✅ Done | `Location`, `Crop`, `FarmerSession` ORM models |
| `Backend/App/schemas.py` | ✅ Done | `LocationOut`, `CropOut`, `AdvisoryInput/Item/Output` |
| `Backend/App/database.py` | ✅ Done | SQLAlchemy engine + session, SQLite |
| `Backend/App/seed.py` | ✅ Done | 5 Gujarat locations with lat/lng, 4 crops |
| `Backend/App/adapters/weather.py` | ✅ Done | Deterministic 7-day forecast per location |
| `Backend/App/engine/advisory.py` | ✅ Done | Stage matching, confidence scoring, plain-language templates |
| `Backend/App/routers/advisory.py` | ✅ Done | `POST /advisory` + `/api/advisory` |
| `Backend/App/routers/rules.py` | ✅ Done | `GET /rules` + `/api/rules` |
| `Backend/App/routers/health.py` | ✅ Done | `GET /health` + `/api/health` |
| `Backend/App/routers/locations.py` | ✅ Done | `GET /locations` + `/api/locations` |
| `Backend/App/routers/crops.py` | ✅ Done | `GET /crops` + `/api/crops` |
| `Backend/data/irrigation_rules.json` | ✅ Done | 4 crops × 4 stages |
| `Backend/data/fertiliser_rules.json` | ✅ Done | 4 crops × 4 stages |
| `Backend/data/pest_rules.json` | ✅ Done | 4 crops × 4 stages |
| `Frontend/src/api.js` | ✅ Done | `get`, `post`, `health`, `locations`, `crops`, `postAdvisory`, `getRules` |
| `Frontend/src/App.jsx` | ✅ Done | View state pattern: home / form / results |
| `Frontend/src/components/AdvisoryForm.jsx` | ✅ Done | Intake form with all fields |
| `Frontend/src/components/AdvisoryResult.jsx` | ✅ Done | 3 advisory cards with expandable details |
| `Frontend/src/components/Layout.jsx` | ✅ Done | Header + footer wrapper |
| `Frontend/src/components/HealthCheck.jsx` | ✅ Done | Backend health display |
| `Frontend/src/components/LocationList.jsx` | ✅ Done | 5 locations card list |
| `Frontend/src/components/CropList.jsx` | ✅ Done | 4 crops card list |
| `Frontend/vite.config.js` | ✅ Done | Proxy configured for all API paths |

### 1.2 What You Must NOT Change

- Location & Crop seed data (5 Gujarat locations, 4 crops)
- Rule JSON files and engine logic (Chunk 2's advisory engine)
- `GET /health`, `GET /locations`, `GET /crops`, `GET /rules` endpoints
- `POST /advisory` endpoint and its schemas
- Existing frontend components (AdvisoryForm, AdvisoryResult, Layout, HealthCheck, etc.)
- Frontend `api.js` existing methods (you will _add_ to it, not change existing)
- Vite proxy config

### 1.3 What You Need to Add

| File | Purpose |
|------|---------|
| `Backend/data/mandi_prices.csv` | Synthetic daily price data for 4 crops × 5 markets |
| `Backend/App/engine/spoilage.py` | Spoilage model — value lost per day per storage condition |
| `Backend/App/engine/transport.py` | Transport cost model — cost-per-km using straight-line distance |
| `Backend/App/engine/decision.py` | Decision engine — computes expected return for Sell/Store/Transport |
| `Backend/App/routers/post_harvest.py` | `POST /post-harvest` endpoint |
| `Backend/App/schemas.py` additions | `PostHarvestInput`, `PostHarvestOutput` Pydantic models |
| `Frontend/src/components/PostHarvestForm.jsx` | Intake form for post-harvest planner |
| `Frontend/src/components/PostHarvestResult.jsx` | Results display with recommendation card |
| `Frontend/src/api.js` additions | `postPostHarvest()` method |
| `Frontend/src/App.jsx` updates | Add 'post-harvest-form' and 'post-harvest-results' views |

### 1.4 File Structure After Chunk 3

```
Backend/
├── App/
│   ├── __init__.py
│   ├── main.py                  # + include post_harvest router
│   ├── database.py              # unchanged
│   ├── models.py                # + PostHarvestSession table
│   ├── schemas.py               # + PostHarvestInput, PostHarvestOutput
│   ├── seed.py                  # unchanged
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── weather.py           # unchanged
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── advisory.py          # unchanged
│   │   ├── spoilage.py          # NEW — spoilage curves
│   │   ├── transport.py         # NEW — transport cost
│   │   └── decision.py          # NEW — sell/store/transport logic
│   └── routers/
│       ├── __init__.py
│       ├── advisory.py          # unchanged
│       ├── crops.py             # unchanged
│       ├── health.py            # unchanged
│       ├── locations.py         # unchanged
│       ├── post_harvest.py      # NEW
│       └── rules.py             # unchanged
├── data/
│   ├── fertiliser_rules.json    # unchanged
│   ├── irrigation_rules.json    # unchanged
│   ├── mandi_prices.csv         # NEW — synthetic price data
│   └── pest_rules.json          # unchanged
├── main.py                      # unchanged
├── requirements.txt             # unchanged
├── Procfile                     # unchanged
└── .gitignore                   # unchanged

Frontend/
├── src/
│   ├── api.js                   # + postPostHarvest()
│   ├── App.jsx                  # + post-harvest view states
│   ├── main.jsx                 # unchanged
│   ├── index.css                # unchanged
│   └── components/
│       ├── AdvisoryForm.jsx     # unchanged
│       ├── AdvisoryResult.jsx   # unchanged
│       ├── CropList.jsx         # unchanged
│       ├── HealthCheck.jsx      # unchanged
│       ├── Layout.jsx           # unchanged
│       ├── LocationList.jsx     # unchanged
│       ├── PostHarvestForm.jsx  # NEW
│       └── PostHarvestResult.jsx # NEW
├── index.html                   # unchanged
├── vite.config.js               # unchanged
├── package.json                 # unchanged
├── postcss.config.js            # unchanged
└── tailwind.config.js           # unchanged
```

---

## 2. Backend — Synthetic Mandi Price Data

**Timeline:** 45 min | **Dependencies:** Location/Crop seed data | **Resources:** None

### 2.1 Data File

Create `Backend/data/mandi_prices.csv` with daily synthetic prices for each (crop × market) combination.

**Markets** (one per location, using the nearest mandi name):

| Location | Market Name |
|----------|-------------|
| Ahmedabad | Ahmedabad APMC |
| Vadodara | Vadodara APMC |
| Surat | Surat APMC |
| Rajkot | Rajkot APMC |
| Anand | Anand APMC |

**Price ranges per crop (₹ per quintal, realistic for Gujarat 2026):**

| Crop | Low (₹/q) | High (₹/q) | Seasonality |
|------|-----------|------------|-------------|
| Cotton | 6,000 | 8,500 | Higher Oct–Dec (post-harvest) |
| Wheat | 2,200 | 3,000 | Higher Mar–May (post-harvest) |
| Groundnut | 5,500 | 7,500 | Higher Oct–Dec |
| Tomato | 1,200 | 2,800 | Higher Dec–Feb, dips in peak season |

**CSV Schema:**

```
date,crop,market,price_per_quintal
2026-01-01,Cotton,Ahmedabad APMC,7200
...
```

Generate ~90 days of data (Jan 1 – Mar 31 2026) for each of the 4 crops × 5 markets = 1,800 rows. Use deterministic prices with a slight upward trend and minor daily variance so charts look realistic.

### 2.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 2.1 | Create `Backend/data/mandi_prices.csv` | 1,800 rows of synthetic price data | File has header + 1800 data rows |
| 2.2 | Write a `load_prices()` helper | Reads CSV, filters by crop + market, returns list of `{date, price}` sorted by date | `python -c "from App.engine.decision import load_prices; print(len(load_prices('Cotton', 'Ahmedabad APMC')))"` returns ~90 |

---

## 3. Backend — Spoilage Model

**Timeline:** 1 hr | **Dependencies:** None | **Resources:** None

### 3.1 Logic

A simple function that estimates how much of the produce value is lost per day, based on crop type and storage condition.

| Storage Condition | Spoilage Rate (%/day) | Max Days Before Total Loss |
|------------------|----------------------|---------------------------|
| `open` | 1.5% / day | 60 days |
| `warehouse` | 0.6% / day | 150 days |
| `cold_storage` | 0.15% / day | 600 days |

**Per-crop modifiers:**

| Crop | Modifier | Reason |
|------|----------|--------|
| Tomato | 2.0× base rate | Perishable, high spoilage |
| Groundnut | 0.7× base rate | Oilseed, lower moisture |
| Cotton | 0.5× base rate | Fibre crop, very low spoilage |
| Wheat | 0.8× base rate | Grain, moderate spoilage if dry |

**Formula:**

```
effective_daily_rate = base_rate × crop_modifier
value_remaining = initial_value × (1 - effective_daily_rate) ^ days_stored
```

### 3.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 3.1 | Create `Backend/App/engine/spoilage.py` | `compute_spoilage(crop: str, storage: str, days: int, initial_value: float) → dict` with `{value_remaining, loss_percent, total_loss}` | Tomato + open + 10 days → ~26% loss |
| 3.2 | Test edge cases | 0 days → 0% loss; very long storage → near-total loss | Sanity-check output |

---

## 4. Backend — Transport Cost Model

**Timeline:** 45 min | **Dependencies:** Location lat/lng from seed data | **Resources:** None

### 4.1 Logic

A simple cost-per-kilometre function using straight-line (Haversine) distance between the farmer's location and each market.

```
distance_km = haversine(lat1, lng1, lat2, lng2)
transport_cost = distance_km × cost_per_km × quantity_in_quintals
```

**Cost parameters:**

| Parameter | Value |
|-----------|-------|
| Cost per km per quintal | ₹5/km/quintal |
| Minimum charge | ₹500 |

**Market coordinates** (use the 5 location lat/lng from seed data):

| Market | Latitude | Longitude |
|--------|----------|-----------|
| Ahmedabad APMC | 23.0225 | 72.5714 |
| Vadodara APMC | 22.3072 | 73.1812 |
| Surat APMC | 21.1702 | 72.8311 |
| Rajkot APMC | 22.3039 | 70.8022 |
| Anand APMC | 22.5645 | 72.9289 |

### 4.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 4.1 | Create `Backend/App/engine/transport.py` | `haversine(lat1, lng1, lat2, lng2) → float` and `transport_cost(lat, lng, quantity) → list[dict]` with cost per market | Known distance → returns ~cost |
| 4.2 | Verify market list | 5 markets returned with distance and cost | Reasonable distances (e.g. Anand→Vadodara ~30km) |

---

## 5. Backend — Decision Engine

**Timeline:** 2 hr | **Dependencies:** 3 (spoilage), 4 (transport), 2 (price data) | **Resources:** None

### 5.1 Logic

The decision engine evaluates 3 options and returns the one with the highest expected net return.

**Option 1 — Sell Now:**
```
nearest_market = find_closest_market(location)
current_price = get_latest_price(crop, nearest_market)
transport = transport_cost(to=nearest_market, quantity)
expected_return = (current_price × quantity) - transport
```

**Option 2 — Store for N days:**
```
store_days = 14 (default recommendation period)
future_price = get_future_price(crop, nearest_market, store_days)
spoilage = compute_spoilage(crop, storage, store_days, future_price × quantity)
expected_return = future_price × quantity - spoilage['total_loss']
storage_cost = store_days × daily_storage_cost  # ₹2/quintal/day warehouse, ₹5 cold storage
expected_return -= storage_cost
```

**Option 3 — Transport to Best Market:**
```
all_markets = get_all_markets()
for each market:
    price = get_latest_price(crop, market)
    transport = transport_cost(to=market, quantity)
    net = price × quantity - transport
pick market with highest net
expected_return = net
```

**Output:**

```python
{
    "recommendation": "sell_now",  # or "store" or "transport"
    "option_label": "Sell Now",
    "expected_return": 78500.0,
    "expected_return_per_quintal": 7850.0,
    "details": {
        "sell_now": {
            "market": "Anand APMC",
            "price_per_quintal": 7200,
            "transport_cost": 1500,
            "net_return": 70500,
            "distance_km": 12.5
        },
        "store": {
            "market": "Anand APMC",
            "store_days": 14,
            "storage": "warehouse",
            "spoilage_loss": 4200,
            "storage_cost": 280,
            "future_price_per_quintal": 7450,
            "net_return": 70020
        },
        "transport": {
            "market": "Ahmedabad APMC",
            "price_per_quintal": 7600,
            "transport_cost": 3500,
            "distance_km": 45.2,
            "net_return": 72500
        }
    },
    "reason": "Transporting to Ahmedabad APMC yields ₹72,500 — ₹2,000 more than selling locally."
}
```

### 5.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 5.1 | Create `Backend/App/engine/decision.py` | `generate_recommendation(crop, quantity, storage, location_lat, location_lng) → dict` | Returns 3 options with valid numbers |
| 5.2 | Implement price lookup helpers | `get_latest_price(crop, market)`, `get_future_price(crop, market, days_from_now)` | Returns realistic ₹ values |
| 5.3 | Implement market distance sorting | Compute transport cost to all 5 markets, sort by net return | Closest market isn't always best |
| 5.4 | Test with sample inputs | Cotton + 10 quintals + warehouse + Anand → returns valid recommendation | No crashes, numbers add up |

---

## 6. Backend — POST /post-harvest Endpoint

**Timeline:** 1 hr | **Dependencies:** 5 (decision engine exists) | **Resources:** None

### 6.1 Pydantic Schemas to Add (`Backend/App/schemas.py`)

```python
class PostHarvestInput(BaseModel):
    crop_name: str
    quantity_quintals: float  # > 0
    storage_condition: str  # "open" | "warehouse" | "cold_storage"
    location_name: str

class OptionDetail(BaseModel):
    market: str
    price_per_quintal: float
    transport_cost: float
    net_return: float
    distance_km: float | None = None

class StoreOption(OptionDetail):
    store_days: int
    storage: str
    spoilage_loss: float
    storage_cost: float
    future_price_per_quintal: float

class PostHarvestOutput(BaseModel):
    recommendation: str  # "sell_now" | "store" | "transport"
    option_label: str
    expected_return: float
    expected_return_per_quintal: float
    details: dict
    reason: str
    session_id: int
```

### 6.2 Endpoint Logic

```
POST /post-harvest
Body: { crop_name, quantity_quintals, storage_condition, location_name }

1. Look up location and crop in DB → 404 if not found
2. Call decision.generate_recommendation(...)
3. Save a PostHarvestSession record with input details
4. Return { recommendation, option_label, expected_return, details, reason, session_id }
```

### 6.3 DB Model to Add (`Backend/App/models.py`)

```python
class PostHarvestSession(Base):
    __tablename__ = "post_harvest_sessions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    crop_id = Column(Integer, ForeignKey("crops.id"))
    quantity_quintals = Column(Float, nullable=False)
    storage_condition = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)  # "sell_now" | "store" | "transport"
    expected_return = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 6.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 6.1 | Add `PostHarvestSession` model to `models.py` | New table for saving post-harvest sessions | |
| 6.2 | Add input/output schemas to `schemas.py` | Pydantic models for request/response | |
| 6.3 | Create `Backend/App/routers/post_harvest.py` | `POST /post-harvest` + `/api/post-harvest` — validates, calls engine, saves session, returns result | |
| 6.4 | Wire router into `main.py` | `app.include_router(post_harvest.router)` | |
| 6.5 | Test with curl | `POST /post-harvest` with valid body → 200 + recommendation | |
| 6.6 | Test validation errors | Missing fields → 422, unknown crop/location → 404 | |
| 6.7 | Add `/post-harvest` to Vite proxy | In `Frontend/vite.config.js` | |

---

## 7. Frontend — Post-Harvest Intake Form

**Timeline:** 2 hr | **Dependencies:** Backend endpoint working | **Resources:** None

### 7.1 Component: `PostHarvestForm.jsx`

A mobile-responsive single-page form following the same visual style as `AdvisoryForm.jsx`.

| Field | Type | Source | Validation |
|-------|------|--------|------------|
| Crop | `<select>` dropdown | Fetched from `GET /crops` | Required |
| Quantity (quintals) | `<input type="number">` | User input | Required, min 0.1, step 0.5 |
| Storage Condition | `<select>` dropdown | Hardcoded: Open Yard, Warehouse, Cold Storage | Required |
| Location | `<select>` dropdown | Fetched from `GET /locations` | Required |
| Submit button | `<button>` | Calls `api.postPostHarvest(...)` | Disabled while submitting |

**States:**
- **Loading:** Spinner while fetching dropdown data
- **Error:** Red error banner if backend unreachable
- **Form:** Ready state with all fields
- **Submitting:** Button shows spinner, all fields disabled
- **Success:** Navigate to post-harvest results view
- **Error on submit:** Red error banner (stay on form)

### 7.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 7.1 | Create `Frontend/src/components/PostHarvestForm.jsx` | Full form component matching `AdvisoryForm.jsx` styling conventions | |
| 7.2 | Add `api.postPostHarvest(data)` to `api.js` | POST to `/post-harvest`, returns JSON with recommendation | |
| 7.3 | Test form manually | Fill fields, submit, verify network request to backend | |
| 7.4 | Mobile-responsive pass | Test at 375px width | |

### 7.3 Storage Condition Options

| Option Value | Display Text |
|-------------|-------------|
| `open` | Open Yard |
| `warehouse` | Warehouse (Covered) |
| `cold_storage` | Cold Storage |

---

## 8. Frontend — Post-Harvest Results Display

**Timeline:** 1.5 hr | **Dependencies:** 7 (form submits successfully) | **Resources:** None

### 8.1 Component: `PostHarvestResult.jsx`

Shows the recommendation in a single prominent card, with expandable "What if I..." sections for the other two options.

**Layout (mobile-first):**

```
┌──────────────────────────────────┐
│  📦 Post-Harvest Plan            │
│  Cotton • 10 quintals            │
│  Warehouse • Anand               │
├──────────────────────────────────┤
│ ┌── Recommended ───────────────┐ │
│ │  🏆 Transport to Ahmedabad   │ │
│ │  APMC                        │ │
│ │  Expected Return             │ │
│ │  ₹72,500                     │ │
│ │  (₹7,250/quintal)            │ │
│ │                              │ │
│ │  Distance: 45 km             │ │
│ │  Transport cost: ₹3,500      │ │
│ │  Market price: ₹7,600/q     │ │
│ │                              │ │
│ │  "Transporting to Ahmedabad  │ │
│ │   APMC yields ₹2,000 more   │ │
│ │   than selling locally."     │ │
│ └──────────────────────────────┘ │
│                                  │
│  [▸ Sell Now (₹70,500)]          │
│  [▸ Store 14 days (₹70,020)]     │
│                                  │
│  [← New Plan]  [Home Dashboard]  │
└──────────────────────────────────┘
```

**Colour coding:**
- Recommended option → green gradient header, prominent ₹ number
- Alternative options → collapsible accordion panels in grey
- Negative values (loss, cost) → red text

### 8.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 8.1 | Create `Frontend/src/components/PostHarvestResult.jsx` | Recommendation card with accordion alternatives | |
| 8.2 | Wire into `App.jsx` | Show `PostHarvestResult` after successful submission | |
| 8.3 | Test with varied inputs | Different crops, quantities, storage conditions produce distinct recommendations | |
| 8.4 | Mobile-responsive pass | Cards stack vertically, tap targets ≥44px | |

---

## 9. Frontend — Navigation & Integration

**Timeline:** 1 hr | **Dependencies:** 7, 8 (form + results exist) | **Resources:** None

### 9.1 View State in `App.jsx`

Augment the existing view-state pattern:

```jsx
const [view, setView] = useState('home')
// 'home' → existing Chunk 1 dashboard
// 'form' → AdvisoryForm (Chunk 2)
// 'results' → AdvisoryResult (Chunk 2)
// 'ph-form' → PostHarvestForm (NEW)
// 'ph-results' → PostHarvestResult (NEW)

const [lastPHResult, setLastPHResult] = useState(null)
const [phInputs, setPHInputs] = useState(null)
```

### 9.2 Homepage Additions

Add a second CTA button on the homepage below the advisory one:

```jsx
<button onClick={() => setView('ph-form')}>
  📦 Plan Post-Harvest
</button>
```

### 9.3 Preserving Chunk 1 & 2 Functionality

- Homepage shows: health check, locations, crops (Chunk 1) + "Get Crop Advisory" button (Chunk 2) + "Plan Post-Harvest" button (Chunk 3)
- Advisory form and results work exactly as before
- Navigation is always: Home ↔ Advisory flow → Home ↔ Post-Harvest flow

### 9.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 9.1 | Update `App.jsx` | Add `ph-form` and `ph-results` view states | |
| 9.2 | Add Post-Harvest CTA to homepage | "Plan Post-Harvest" button below "Get Crop Advisory" | |
| 9.3 | Verify Chunk 1 still works | Homepage shows health + locations + crops | |
| 9.4 | Verify Chunk 2 still works | Advisory form submits and shows results | |

---

## 10. Edge Case Handling & Combination Test

**Timeline:** 1 hr | **Dependencies:** All above

### 10.1 Edge Cases to Handle

| Scenario | Expected Behavior |
|----------|------------------|
| Zero/negative quantity | API returns 422 validation error |
| Unknown crop name | API returns 404 with clear message |
| Unknown location name | API returns 404 with clear message |
| Invalid storage condition | API returns 422 (validation) |
| Very large quantity (1000+ quintals) | Transport costs scale linearly, no overflow |
| Farmer location same as market | Transport cost = minimum ₹500 |
| All markets have same price | Sell Now recommended (no transport benefit) |
| Future price not in CSV | Fall back to latest available price |
| CSV file missing | Engine catches error, returns 500 with clear message |

### 10.2 Test Matrix

Test at least 8 combinations covering different crops, quantities, storage conditions, and locations:

| # | Crop | Qty | Storage | Location | Expected |
|---|------|-----|---------|----------|----------|
| 1 | Cotton | 10 | warehouse | Anand | Valid recommendation |
| 2 | Tomato | 5 | open | Ahmedabad | Sell soon (high spoilage) |
| 3 | Wheat | 20 | cold_storage | Vadodara | Store likely best |
| 4 | Groundnut | 8 | warehouse | Rajkot | Valid recommendation |
| 5 | Tomato | 15 | cold_storage | Surat | Transport may beat local |
| 6 | Cotton | 50 | warehouse | Vadodara | Large qty → transport matters |
| 7 | Groundnut | 3 | open | Anand | Small qty → sell local |
| 8 | Wheat | 100 | cold_storage | Rajkot | Bulk + cold storage → store |

For each combo verify:
1. HTTP 200 response
2. `recommendation` is one of "sell_now", "store", "transport"
3. `expected_return` is a positive number
4. `reason` is a non-empty string explaining the choice
5. All 3 options have valid numbers in `details`

### 10.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 10.1 | Run 8-combo test | Script or manual POST for all combos | All return 200 with valid recommendation |
| 10.2 | Test edge cases from §10.1 | Each edge case | Correct error/fallback behavior |
| 10.3 | Fix any crashes or bad output | Iterate on engine until clean | Re-test 8 combos after fixes |

---

## 11. Deploy & Smoke Test

**Timeline:** 45 min | **Dependencies:** All above merged and tested

### 11.1 Smoke Test Checklist

- [ ] `GET /health` → 200
- [ ] `GET /locations` → 5 locations returned
- [ ] `GET /crops` → 4 crops returned
- [ ] `POST /post-harvest` with valid body → 200 + recommendation
- [ ] `POST /post-harvest` with invalid body → 4xx error
- [ ] `POST /advisory` still works (Chunk 2 regression)
- [ ] Frontend homepage loads with both CTA buttons
- [ ] "Get Crop Advisory" → form → submit → results (Chunk 2 intact)
- [ ] "Plan Post-Harvest" → form → submit → recommendation
- [ ] Responsive at 375px on all screens
- [ ] No new external dependencies added

### 11.2 Implementation Tasks

| # | Task | Description |
|---|------|-------------|
| 11.1 | Push backend changes → verify on Render | All endpoints respond |
| 11.2 | Push frontend changes → verify on Vercel | All views render |
| 11.3 | Run full smoke test | Complete §11.1 checklist |
| 11.4 | Write handoff note for P4 | |

---

## 12. Done Criteria Checklist

- [ ] `POST /post-harvest` returns a Sell / Store / Transport recommendation for all tested combos
- [ ] Recommendation includes expected-return number (₹) and per-quintal value
- [ ] Response includes details for all 3 options (sell_now, store, transport) with ₹ costs
- [ ] `reason` field explains the recommendation in plain language
- [ ] Spoilage model: different rates per storage condition, crop-specific modifiers
- [ ] Transport cost model: distance-based cost using Haversine, 5 markets
- [ ] Decision engine: compares 3 options, picks highest net return
- [ ] Synthetic `mandi_prices.csv` covers 4 crops × 5 markets × ~90 days
- [ ] `PostHarvestSession` saved to DB on each request (persistence)
- [ ] `PostHarvestForm.jsx` — crop, quantity, storage, location fields with validation
- [ ] `PostHarvestResult.jsx` — prominent recommendation card + expandable alternatives
- [ ] Homepage has both "Get Crop Advisory" and "Plan Post-Harvest" CTA buttons
- [ ] Chunk 1 homepage still works (health + locations + crops)
- [ ] Chunk 2 advisory flow still works end-to-end
- [ ] Frontend handles: loading, empty, error, and success states on both pages
- [ ] Backend handles: missing fields (422), unknown crop/location (404)
- [ ] Mobile-responsive at 375px on all new screens
- [ ] Deployed on Vercel + Render, full flow works end-to-end
- [ ] No ORM changes beyond adding one table, no state management, no Docker added
- [ ] Vite proxy config includes `/post-harvest`

---

## 13. Handoff to P4 Template

```
Built Module B — Post-Harvest Loss Planner on top of Chunks 1 & 2.

📍 Intake form at / → "Plan Post-Harvest" → dropdowns for crop, location,
   storage condition (open/warehouse/cold_storage), quantity input
📦 POST /post-harvest returns a Sell / Store / Transport recommendation
   with expected-return ₹ amount, per-quintal value, and plain-language reason
📊 Decision engine compares 3 options:
   - Sell Now (current price at nearest market − transport)
   - Store for 14 days (future price − spoilage − storage cost)
   - Transport to best market (highest price − transport cost)
🧮 Spoilage model: daily loss rate × crop modifier × storage condition
🚚 Transport model: Haversine distance × ₹5/km/quintal
📈 Synthetic price data in Backend/data/mandi_prices.csv — 4 crops × 5 markets × 90 days
🧪 Tested across 8+ crop/quantity/storage/location combinations

To test Chunk 3 is good:
→ Open frontend → "Plan Post-Harvest"
→ Pick Cotton + 10 + Warehouse + Anand → Submit
→ See recommendation card with ₹ amount + reason
→ Expand "Sell Now" and "Store" alternatives
→ Go back, click "Get Crop Advisory" — Chunk 2 still works

Your work (Chunk 4) starts in:
Frontend/src/App.jsx — add combined dashboard view
Frontend/src/components/ — add Dashboard.jsx (side-by-side view)
Frontend/ — add Recharts for spoilage + price trend charts
Docs/ — finalize README with screenshots

Chunks 1 & 2 are both fully intact — health check, locations, crops,
advisory form all still work.
```

---

## 14. Ponytail Simplification Log

| Shortcut | Skipped | Add When | Location |
|----------|---------|----------|----------|
| No Haversine library | `math` stdlib (`sin`, `cos`, `sqrt`, `atan2`) | Never — stdlib is sufficient | `Backend/App/engine/transport.py` |
| No pandas for CSV | `csv` stdlib + manual parsing | CSV has 1,800 rows, stdlib is fine | `Backend/App/engine/decision.py` |
| No real price API | Synthetic CSV data | Phase 1 — Chunk 5 (real data swap-in) | `Backend/data/mandi_prices.csv` |
| No real storage cost | Hardcoded ₹2 & ₹5/quintal/day | Phase 2 — real partner data | `Backend/App/engine/decision.py` |
| No charts on this page | Recharts line charts | Chunk 4 — combined dashboard | `Frontend/src/components/PostHarvestResult.jsx` |
| No route library | Simple view-state in App.jsx | When 6+ views exist | `Frontend/src/App.jsx` |
| No test framework | Manual curl + 8-combo test | Chunk 8 — Week 2 hardening | Not applicable |
| Static spoilage curves | ML-based spoilage prediction | Phase 2 — real field data | `Backend/App/engine/spoilage.py` |
| No state management | useState in App.jsx | Form state persistence issues | `Frontend/src/App.jsx` |

---

## 15. Resource Summary

| Resource | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime (unchanged) |
| FastAPI | 0.110+ | REST API framework (unchanged) |
| SQLAlchemy | 2.0+ | ORM (unchanged) |
| Pydantic | 2.x | Input/output validation (unchanged) |
| Node.js | 18+ | Frontend runtime (unchanged) |
| React | 18+ | UI library (unchanged) |
| Vite | 5+ | Build tool (unchanged) |
| Tailwind CSS | 3+ | Utility CSS (unchanged) |
| SQLite | 3.x | Embedded database (unchanged) |
| Vercel | — | Frontend hosting (unchanged) |
| Render | — | Backend hosting (unchanged) |
| **New: math** | stdlib | Haversine distance (sin, cos, sqrt, atan2) |
| **New: csv** | stdlib | Reading mandi_prices.csv |
| **New: statistics** | stdlib | Mean price calculations |

No new external dependencies. Everything uses Python stdlib (`math`, `csv`, `statistics`) plus what Chunks 1 & 2 already installed.

---

## 16. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Haversine formula has edge case at antipodal points | Very Low | Low | All 5 locations are within Gujarat (~300km radius) — no antipodal risk |
| Price CSV has 1,800 rows — parsing too slow for endpoint | Low | Low | Load once into memory on first call, cache in module-level dict |
| Spoilage formula produces negative value | Low | Medium | Clamp: `max(0, value_remaining)` |
| Recommendation always says "Sell Now" (boring) | Medium | Low | Tune price data so storage/transport sometimes win — test with §10.2 matrix |
| Frontend form uses different styling than AdvisoryForm | Medium | Low | Copy the exact Tailwind class patterns from AdvisoryForm.jsx |
| Transport cost to same-location market is zero | Low | Low | Minimum charge of ₹500 ensures non-zero cost |
| Breaking Chunk 2 advisory flow | Medium | High | Never modify existing files — only add new ones; re-test after every step |
| Vite proxy doesn't forward `/post-harvest` | Low | Medium | Add to proxy config in `vite.config.js` |

---

## 17. Milestone Summary

| Milestone | Time | Gate |
|-----------|------|------|
| M1 — `mandi_prices.csv` created with 4 crops × 5 markets × 90 days | T+45 min | File has 1,800 rows, parseable with `csv.DictReader` |
| M2 — Spoilage model returns correct loss % for all 3 storage types | T+1.5 hr | `python -c "from App.engine.spoilage import compute_spoilage; print(compute_spoilage('Tomato', 'open', 10, 10000))"` |
| M3 — Transport model returns distances + costs for 5 markets | T+2.25 hr | Known distance (Anand→Vadodara ≈ 30km) matches ~₹150 transport for 1 quintal |
| M4 — Decision engine returns recommendation for 1 input | T+3.5 hr | `python -c "from App.engine.decision import generate_recommendation; print(generate_recommendation('Cotton', 10, 'warehouse', 22.56, 72.93))"` |
| M5 — `POST /post-harvest` returns 200 on curl | T+4.5 hr | `curl -X POST ...` returns recommendation |
| M6 — Post-harvest form renders and submits in browser | T+6 hr | Full frontend flow works locally |
| M7 — 8-combo test passes + edge cases verified | T+7 hr | All combos return valid recommendations |
| M8 — Deployed, smoke test passed, handoff written | T+8 hr | P4 can start immediately |
