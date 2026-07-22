# Chunk 5 — Execution Plan

## Real Data — Weather & Market Prices

| Field | Value |
|-------|-------|
| **Owner** | Dhruvin (P1) |
| **Phase** | Phase 1 — Hackathon MVP |
| **Depends on** | Chunk 4 (Unified Dashboard, all Phase 0 features live, deployed on Vercel + Render) |
| **Deliverable** | Live OpenWeatherMap weather integration + live Agmarknet/data.gov.in mandi price integration, both with silent fallback to mocked data on failure; all existing Module A & B features remain 100% functional |
| **PRD Ref** | §7.1 (FR-A2), §7.2 (FR-B2), §9.1 (Data Layer), §10 (Data Requirements & Sources), §13.1 (Risks — API downtime) |
| **Chunk Plan Ref** | Full Phase Chunk Plan § Chunk 5 |

---

## Table of Contents

1. [Pre-Flight Audit — What Chunk 4 Left You](#1-pre-flight-audit--what-chunk-4-left-you)
2. [Hackathon Problem Statement Review](#2-hackathon-problem-statement-review)
3. [Backend — Live Weather API Adapter (OpenWeatherMap)](#3-backend--live-weather-api-adapter-openweathermap)
4. [Backend — Weather Fallback Layer](#4-backend--weather-fallback-layer)
5. [Backend — Live Mandi Price Adapter (Agmarknet / data.gov.in)](#5-backend--live-mandi-price-adapter-agmarknet--datagovin)
6. [Backend — Price Fallback Layer](#6-backend--price-fallback-layer)
7. [Backend — Adapter Health Endpoint](#7-backend--adapter-health-endpoint)
8. [Frontend — Data Source Indicator](#8-frontend--data-source-indicator)
9. [Testing — Fallback Verification & Edge Cases](#9-testing--fallback-verification--edge-cases)
10. [Deployment & Integration Verification](#10-deployment--integration-verification)
11. [Done Criteria Checklist](#11-done-criteria-checklist)
12. [Handoff to P2 Template](#12-handoff-to-p2-template)
13. [Ponytail Simplification Log](#13-ponytail-simplification-log)
14. [Resource Summary](#14-resource-summary)
15. [Risk Register](#15-risk-register)
16. [Milestone Summary](#16-milestone-summary)

---

## 1. Pre-Flight Audit — What Chunk 4 Left You

Before building anything in Chunk 5, perform a complete audit of the repository state handed over by Chunk 4 (Mithil).

### 1.1 What Exists (Phase 0 Deliverables)

| Component / File | Status | Description / Capability |
|------------------|--------|--------------------------|
| `Backend/App/main.py` | ✅ Done | FastAPI application wiring routers for health, locations, crops, advisory, rules, and post-harvest |
| `Backend/App/models.py` | ✅ Done | ORM models: `Location`, `Crop`, `FarmerSession`, `PostHarvestSession` |
| `Backend/App/schemas.py` | ✅ Done | Pydantic schemas: `AdvisoryInput/Output`, `PostHarvestInput/Output` |
| `Backend/App/database.py` | ✅ Done | SQLite engine and session factory |
| `Backend/App/seed.py` | ✅ Done | 5 seeded Gujarat locations (Ahmedabad, Vadodara, Surat, Rajkot, Anand) & 4 crops (Cotton, Wheat, Groundnut, Tomato) |
| `Backend/App/adapters/weather.py` | ✅ Done | **Deterministic 7-day weather forecast per location** (THIS IS WHAT YOU REPLACE) |
| `Backend/App/engine/advisory.py` | ✅ Done | Stage-matching advisory ranking engine with confidence scoring |
| `Backend/App/engine/spoilage.py` | ✅ Done | Spoilage model calculating daily value decay per storage condition & crop modifier |
| `Backend/App/engine/transport.py` | ✅ Done | Haversine straight-line distance and cost model (₹5/km/q, ₹500 min) |
| `Backend/App/engine/decision.py` | ✅ Done | Post-harvest decision engine comparing Sell Now, Store, and Transport options (uses `mandi_prices.csv`) |
| `Backend/App/routers/post_harvest.py` | ✅ Done | `POST /post-harvest` REST endpoint |
| `Backend/data/mandi_prices.csv` | ✅ Done | 1,800 rows of daily market prices across 4 crops × 5 APMC markets × 90 days (THIS IS WHAT YOU AUGMENT) |
| `Frontend/src/api.js` | ✅ Done | Centralized API client |
| `Frontend/src/App.jsx` | ✅ Done | Single-page state router with `dashboard` view |
| `Frontend/src/components/Dashboard.jsx` | ✅ Done | Unified side-by-side dashboard |
| `Frontend/src/components/SpoilageChart.jsx` | ✅ Done | Recharts spoilage decay curve |
| `Frontend/src/components/PriceTrendChart.jsx` | ✅ Done | Recharts mandi price trends |
| `Docs/handoff-to-p1-phase1.md` | ✅ Done | Phase 0 → Phase 1 transition instructions |

### 1.2 What You Must NOT Change

To preserve complete system stability across all Phase 0 features:
- **Do NOT alter** existing backend database schemas or ORM models (`Location`, `Crop`, `FarmerSession`, `PostHarvestSession`).
- **Do NOT modify** core decision logic in `advisory.py`, `spoilage.py`, `transport.py`, or `decision.py` — only change data *sources*, not data *consumers*.
- **Do NOT break or remove** existing API endpoints (`/health`, `/locations`, `/crops`, `/advisory`, `/post-harvest`, `/rules`).
- **Do NOT overwrite or delete** any frontend components (`Dashboard.jsx`, `AdvisoryForm.jsx`, `PostHarvestForm.jsx`, etc.).
- **Do NOT introduce** heavy ML dependencies (PyTorch, TensorFlow) — that is Chunk 6's responsibility.

### 1.3 What You Need to Add in Chunk 5

| Target File | Purpose & Responsibility |
|-------------|--------------------------|
| `Backend/App/adapters/weather.py` | **REWRITE:** Add live OpenWeatherMap API call with silent fallback to deterministic mock |
| `Backend/App/adapters/market_prices.py` | **NEW:** Live Agmarknet/data.gov.in price adapter with silent fallback to `mandi_prices.csv` |
| `Backend/App/adapters/config.py` | **NEW:** API keys and adapter configuration via environment variables |
| `Backend/App/routers/advisory.py` | Minor update: wire new weather adapter (same interface, no signature change) |
| `Backend/App/engine/decision.py` | Minor update: wire new market price adapter (same interface, no signature change) |
| `Backend/requirements.txt` | Add `httpx` for async HTTP calls to external APIs |
| `Frontend/src/components/DataStatusIndicator.jsx` | **NEW:** Subtle indicator showing whether live or mocked data is in use |
| `Docs/chunk-5-execution-plan.md` | THIS DOCUMENT |

### 1.4 File Structure After Chunk 5 Completion

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
│   │   │   ├── __init__.py
│   │   │   ├── weather.py              # REWRITTEN — Live OpenWeatherMap + mock fallback
│   │   │   ├── market_prices.py        # NEW — Live Agmarknet + CSV fallback
│   │   │   └── config.py               # NEW — API keys from env vars
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── advisory.py
│   │   │   ├── spoilage.py
│   │   │   ├── transport.py
│   │   │   └── decision.py             # Updated to use market_prices adapter
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── advisory.py
│   │       ├── crops.py
│   │       ├── health.py
│   │       ├── locations.py
│   │       ├── post_harvest.py
│   │       └── rules.py
│   ├── data/
│   │   ├── fertiliser_rules.json
│   │   ├── irrigation_rules.json
│   │   ├── mandi_prices.csv            # Retained as fallback
│   │   └── pest_rules.json
│   ├── requirements.txt                # + httpx
│   └── Procfile
├── Frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── AdvisoryForm.jsx
│   │       ├── AdvisoryResult.jsx
│   │       ├── CropList.jsx
│   │       ├── Dashboard.jsx
│   │       ├── HealthCheck.jsx
│   │       ├── Layout.jsx
│   │       ├── LocationList.jsx
│   │       ├── PostHarvestForm.jsx
│   │       ├── PostHarvestResult.jsx
│   │       ├── PriceTrendChart.jsx
│   │       ├── SpoilageChart.jsx
│   │       ├── UnifiedScenarioForm.jsx
│   │       └── DataStatusIndicator.jsx  # NEW — Live/Mock status badge
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── postcss.config.js
│   └── tailwind.config.js
├── Docs/
│   ├── architecture.md
│   ├── chunk-1-execution-plan.md
│   ├── chunk-2-execution-plan.md
│   ├── chunk-3-execution-plan.md
│   ├── chunk-3-completion-report.md
│   ├── chunk-4-execution-plan.md
│   ├── chunk-5-execution-plan.md        # THIS DOCUMENT
│   ├── handoff-to-p4.md
│   ├── handoff-to-p1-phase1.md
│   ├── TetraTHON_2026_Pitch_Deck.md
│   └── user_flows.md
├── Readme.md
└── render.yaml
```

---

## 2. Hackathon Problem Statement Review

**Dependencies:** None

Before writing any code, read the full hackathon problem statement received at the July 31 inauguration. Note any changes from the pre-screening brief:

| Item | Pre-Screening Assumption | Verify Against Full Brief |
|------|--------------------------|---------------------------|
| Weather source | OpenWeatherMap or IMD | Confirm which API is preferred/required |
| Price source | Agmarknet / data.gov.in | Confirm data format and access method |
| Number of crops | 4 minimum | Confirm if more crops are expected |
| Number of locations | 5 minimum | Confirm if more locations are expected |
| Leaf classifier | Stretch goal | Confirm if now a Must-priority requirement |
| SMS/WhatsApp alerts | Simulated | Confirm if real integration is now required |

### 2.1 Implementation Tasks

| # | Task | Description | Output |
|---|------|-------------|--------|
| 2.1 | Read full problem statement | Note every difference from pre-screening brief | Annotation list |
| 2.2 | Update chunk scope if needed | Adjust deliverables if hackathon brief changes requirements | Updated task list |
| 2.3 | Confirm API access requirements | Check if organisers provide API keys or if team must self-register | API key status |

---

## 3. Backend — Live Weather API Adapter (OpenWeatherMap)

**Dependencies:** 2 (problem statement reviewed) | **Resources:** OpenWeatherMap free API key

### 3.1 API Registration

1. Sign up at https://openweathermap.org/api
2. Generate a free API key (free tier: 60 calls/min, 1,000,000 calls/month — more than sufficient)
3. Store the API key as an environment variable: `OPENWEATHER_API_KEY`

### 3.2 Configuration Module (`Backend/App/adapters/config.py`)

Create a central configuration module for all adapter settings:

```python
import os

# OpenWeatherMap
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
OPENWEATHER_TIMEOUT = 5  # seconds

# Agmarknet / data.gov.in
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY", "")
AGMARKNET_BASE_URL = "https://api.data.gov.in/resource"
AGMARKNET_TIMEOUT = 5  # seconds

# Fallback control
WEATHER_FALLBACK_ENABLED = True
PRICE_FALLBACK_ENABLED = True
```

### 3.3 Location Coordinate Mapping

Add latitude/longitude for each seeded location (needed for OpenWeatherMap API calls):

| Location | Latitude | Longitude | OpenWeatherMap `lat`/`lon` |
|----------|----------|-----------|----------------------------|
| Ahmedabad | 23.0225 | 72.5714 | `lat=23.0225&lon=72.5714` |
| Vadodara | 22.3072 | 73.1812 | `lat=22.3072&lon=73.1812` |
| Surat | 21.1702 | 72.8311 | `lat=21.1702&lon=72.8311` |
| Rajkot | 22.3039 | 70.8022 | `lat=22.3039&lon=70.8022` |
| Anand | 22.5645 | 72.9289 | `lat=22.5645&lon=72.9289` |

### 3.4 Live Weather Adapter Rewrite (`Backend/App/adapters/weather.py`)

Replace the deterministic mock with a live-first, fallback-safe adapter:

```python
import datetime
import httpx
from .config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, OPENWEATHER_TIMEOUT

# Retain the original LOCATION_WEATHER dict as FALLBACK_DATA
LOCATION_WEATHER = {
    "Vadodara": { ... },  # Keep existing mock data
    "Anand": { ... },
    "Rajkot": { ... },
    "Ahmedabad": { ... },
    "Surat": { ... }
}

LOCATION_COORDS = {
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Rajkot": {"lat": 22.3039, "lon": 70.8022},
    "Anand": {"lat": 22.5645, "lon": 72.9289},
}

def _fetch_live_forecast(location: str) -> dict | None:
    """Attempt to fetch 7-day forecast from OpenWeatherMap. Returns None on failure."""
    if not OPENWEATHER_API_KEY:
        return None
    
    coords = LOCATION_COORDS.get(location)
    if not coords:
        return None
    
    try:
        with httpx.Client(timeout=OPENWEATHER_TIMEOUT) as client:
            resp = client.get(OPENWEATHER_BASE_URL, params={
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt": 7  # 7-day forecast
            })
            resp.raise_for_status()
            data = resp.json()
            
            # Parse OpenWeatherMap 5-day/3-hour forecast into daily format
            forecast = _parse_owm_forecast(data)
            return {"location": location, "forecast": forecast, "source": "live"}
    except Exception:
        return None

def _parse_owm_forecast(data: dict) -> list[dict]:
    """Convert OpenWeatherMap 3-hour forecast blocks into daily summaries."""
    daily = {}
    for item in data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {
                "temps": [], "humidity": [], "wind": [], "rain": []
            }
        daily[date]["temps"].append(item["main"]["temp"])
        daily[date]["humidity"].append(item["main"]["humidity"])
        daily[date]["wind"].append(item["wind"]["speed"] * 3.6)  # m/s to kph
        pop = item.get("pop", 0) * 100
        daily[date]["rain"].append(pop)
    
    forecast = []
    for i, (date, vals) in enumerate(sorted(daily.items())[:7], 1):
        forecast.append({
            "day": i,
            "date": date,
            "temp_high": round(max(vals["temps"])),
            "temp_low": round(min(vals["temps"])),
            "rain_chance": round(sum(vals["rain"]) / len(vals["rain"])),
            "humidity": round(sum(vals["humidity"]) / len(vals["humidity"])),
            "wind_kph": round(sum(vals["wind"]) / len(vals["wind"]))
        })
    return forecast

def get_forecast(location: str) -> dict:
    """
    Returns 7-day weather forecast. Attempts live API first, falls back to mock.
    """
    if not location:
        raise ValueError("Location name cannot be empty")
    
    matched_location = next(
        (loc for loc in LOCATION_WEATHER if loc.lower() == location.strip().lower()),
        None
    )
    if not matched_location:
        raise ValueError(f"Unknown location: {location}")
    
    # Attempt live API
    live_result = _fetch_live_forecast(matched_location)
    if live_result:
        return live_result
    
    # Fallback to deterministic mock
    return _get_mock_forecast(matched_location)

def _get_mock_forecast(location: str) -> dict:
    """Original deterministic mock forecast (unchanged from Phase 0)."""
    config = LOCATION_WEATHER[location]
    forecast = []
    base_date = datetime.date.today()
    for i in range(1, 8):
        forecast_date = base_date + datetime.timedelta(days=i)
        day_offset = (i - 1) % 3 - 1
        forecast.append({
            "day": i,
            "date": forecast_date.isoformat(),
            "temp_high": config["temp_high"] + day_offset,
            "temp_low": config["temp_low"] + day_offset,
            "rain_chance": config["rain_chances"][i - 1],
            "humidity": min(100, max(0, config["humidity"] + day_offset * 3)),
            "wind_kph": max(0, config["wind_kph"] + day_offset)
        })
    return {"location": location, "forecast": forecast, "source": "mock"}
```

### 3.5 Key Design Principle — Same Interface, No Signature Change

The `get_forecast(location: str) -> dict` function signature remains **identical**. The only change is that the returned dict now includes a `"source": "live" | "mock"` field. No other file in the codebase needs to change its call to this function.

### 3.6 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 3.1 | Create `Backend/App/adapters/config.py` | Environment variable loader for API keys | File exists, reads env vars |
| 3.2 | Add `LOCATION_COORDS` dict to `weather.py` | Lat/lon for 5 seeded locations | Coordinates match `seed.py` |
| 3.3 | Implement `_fetch_live_forecast()` | httpx call to OpenWeatherMap with 5s timeout | Returns parsed forecast or None |
| 3.4 | Implement `_parse_owm_forecast()` | Convert 3-hour blocks to daily summaries | 7-day output matches mock format |
| 3.5 | Rewrite `get_forecast()` | Try live first → fallback to mock | Returns same dict shape + `source` field |
| 3.6 | Retain `_get_mock_forecast()` | Original deterministic logic preserved exactly | Mock output identical to Phase 0 |
| 3.7 | Add `httpx` to `requirements.txt` | `httpx>=0.27` | `pip install -r requirements.txt` succeeds |

---

## 4. Backend — Weather Fallback Layer

**Dependencies:** 3 (live adapter built) | **Resources:** None

### 4.1 Fallback Requirements (PRD §FR-X3, §8)

| Failure Mode | Expected Behavior |
|--------------|-------------------|
| No API key set | Use mock data silently |
| API timeout (>5s) | Use mock data silently |
| API returns 4xx/5xx | Use mock data silently |
| Network unavailable | Use mock data silently |
| API response malformed | Use mock data silently |

**Critical rule:** The user must NEVER see an error screen. The fallback must be invisible to the end user.

### 4.2 Logging for Debugging

Add a Python `logger` call when fallback activates (for developer debugging, not user-visible):

```python
import logging
logger = logging.getLogger(__name__)

# Inside get_forecast():
if live_result:
    logger.info(f"Weather: live data used for {matched_location}")
else:
    logger.warning(f"Weather: fallback to mock for {matched_location}")
```

### 4.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 4.1 | Add logging to `get_forecast()` | Log source selection (live vs mock) | Logs appear in backend console |
| 4.2 | Test with invalid API key | Set `OPENWEATHER_API_KEY=invalid` | App uses mock, warning logged |
| 4.3 | Test with no network | Disconnect internet | App uses mock, warning logged |
| 4.4 | Test with valid API key | Set real key | App uses live data, info logged |

---

## 5. Backend — Live Mandi Price Adapter (Agmarknet / data.gov.in)

**Dependencies:** 3 (weather adapter done) | **Resources:** Agmarknet/data.gov.in API or bulk CSV download

### 5.1 Data Source Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Option A: data.gov.in API** | REST API with API key, filtered by crop/state | Always fresh, programmatic | Rate limits, requires API key |
| **Option B: Bulk CSV download** | Download Agmarknet daily CSV and refresh periodically | Simple, no rate limits | Manual refresh, stale data |
| **Option C: Hybrid** | Try API first, fall back to local CSV | Best of both | Slightly more code |

**Recommended:** Option C (Hybrid) — try live API, fall back to `mandi_prices.csv`.

### 5.2 Market Name Mapping

The existing `mandi_prices.csv` uses market names like `Ahmedabad APMC`. Map these to Agmarknet identifiers:

| CSV Market Name | Agmarknet Market ID | State |
|-----------------|---------------------|-------|
| Ahmedabad APMC | GJ001 | Gujarat |
| Vadodara APMC | GJ002 | Gujarat |
| Surat APMC | GJ003 | Gujarat |
| Rajkot APMC | GJ004 | Gujarat |
| Anand APMC | GJ005 | Gujarat |

### 5.3 Live Price Adapter (`Backend/App/adapters/market_prices.py`)

```python
import csv
import datetime
import httpx
from pathlib import Path
from .config import AGMARKNET_API_KEY, AGMARKNET_BASE_URL, AGMARKNET_TIMEOUT

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "mandi_prices.csv"

MARKET_IDS = {
    "Ahmedabad APMC": "GJ001",
    "Vadodara APMC": "GJ002",
    "Surat APMC": "GJ003",
    "Rajkot APMC": "GJ004",
    "Anand APMC": "GJ005",
}

# Module-level cache for live prices
_live_prices_cache = {}
_csv_prices_cache = {}

def _fetch_live_prices(crop: str, market: str) -> list[dict] | None:
    """Attempt to fetch prices from data.gov.in API. Returns None on failure."""
    if not AGMARKNET_API_KEY:
        return None
    
    market_id = MARKET_IDS.get(market)
    if not market_id:
        return None
    
    try:
        with httpx.Client(timeout=AGMARKNET_TIMEOUT) as client:
            resp = client.get(AGMARKNET_BASE_URL, params={
                "api-key": AGMARKNET_API_KEY,
                "format": "json",
                "filters[commodity]": crop,
                "filters[market]": market,
                "limit": 90  # Last 90 days
            })
            resp.raise_for_status()
            data = resp.json()
            
            records = []
            for record in data.get("records", []):
                records.append({
                    "date": record.get("date", ""),
                    "price": float(record.get("modal_price", 0)),
                    "price_per_quintal": float(record.get("modal_price", 0))
                })
            
            records.sort(key=lambda x: x["date"])
            return records if records else None
    except Exception:
        return None

def load_prices(crop: str, market: str) -> list[dict]:
    """
    Returns price series for crop at market. Tries live API first, falls back to CSV.
    """
    crop = crop.strip().capitalize() if crop else ""
    market = market.strip() if market else ""
    
    cache_key = (crop, market)
    
    # Try live API first
    live_data = _fetch_live_prices(crop, market)
    if live_data:
        _live_prices_cache[cache_key] = live_data
        return live_data
    
    # Fallback to CSV (original logic)
    if cache_key in _csv_prices_cache:
        return _csv_prices_cache[cache_key]
    
    if not CSV_PATH.exists():
        return []
    
    if not _csv_prices_cache:
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["crop"].strip().capitalize(), row["market"].strip())
                price_val = float(row["price_per_quintal"])
                if key not in _csv_prices_cache:
                    _csv_prices_cache[key] = []
                _csv_prices_cache[key].append({
                    "date": row["date"],
                    "price": price_val,
                    "price_per_quintal": price_val
                })
        for key in _csv_prices_cache:
            _csv_prices_cache[key].sort(key=lambda x: x["date"])
    
    return _csv_prices_cache.get(cache_key, [])

# Keep existing helper functions unchanged
def get_latest_price(crop: str, market: str) -> float:
    prices = load_prices(crop, market)
    if not prices:
        return 0.0
    target_idx = max(0, len(prices) - 15)
    return prices[target_idx]["price"]

def get_future_price(crop: str, market: str, days_from_now: int) -> float:
    prices = load_prices(crop, market)
    if not prices:
        return 0.0
    target_idx = max(0, len(prices) - 15)
    future_idx = target_idx + days_from_now
    if future_idx < len(prices):
        return prices[future_idx]["price"]
    return prices[-1]["price"]
```

### 5.4 Wire into Decision Engine

Update `Backend/App/engine/decision.py` to import from the new adapter:

```python
# Change this:
from .transport import MARKETS, haversine, transport_cost
from .spoilage import compute_spoilage

# To this:
from ..adapters.market_prices import get_latest_price, get_future_price
from .transport import MARKETS, haversine, transport_cost
from .spoilage import compute_spoilage
```

Remove the local `load_prices`, `get_latest_price`, and `get_future_price` functions from `decision.py` since they now live in the adapter.

### 5.5 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 5.1 | Create `Backend/App/adapters/market_prices.py` | Live price adapter with CSV fallback | File created |
| 5.2 | Implement `_fetch_live_prices()` | httpx call to data.gov.in with 5s timeout | Returns parsed records or None |
| 5.3 | Implement `load_prices()` | Try live → fallback to CSV | Same return format as Phase 0 |
| 5.4 | Retain `get_latest_price()` and `get_future_price()` | Same interface, now powered by adapter | Decision engine output unchanged |
| 5.5 | Update `decision.py` imports | Remove local price functions, import from adapter | No logic change in decision engine |
| 5.6 | Test with valid API key | Live prices returned | `source: "live"` in response |
| 5.7 | Test with invalid key / no network | CSV fallback used | `source: "mock"` in response |

---

## 6. Backend — Price Fallback Layer

**Dependencies:** 5 (live adapter built) | **Resources:** None

### 6.1 Fallback Requirements

Same as weather — the user must never see an error. If the live price API fails:

1. Log a warning for developer debugging
2. Fall back to `mandi_prices.csv` silently
3. Return data in the exact same format

### 6.2 Data Freshness Consideration

The CSV fallback contains 90 days of historical data. During the demo, this is sufficient to show trends. In production, the CSV would be refreshed daily via a cron job.

### 6.3 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 6.1 | Add logging to `load_prices()` | Log source selection | Logs appear in backend console |
| 6.2 | Test with invalid API key | CSV fallback used silently | App works, warning logged |
| 6.3 | Test with no network | CSV fallback used silently | App works, warning logged |
| 6.4 | Verify decision engine output | Same recommendations as Phase 0 | No regression in Sell/Store/Transport logic |

---

## 7. Backend — Adapter Health Endpoint

**Dependencies:** 3, 5 (both adapters built) | **Resources:** None

### 7.1 Extend `/health` Endpoint

Add adapter status to the existing health check so developers can quickly verify which data sources are active:

```python
# In Backend/App/routers/health.py
from ..adapters.weather import get_forecast
from ..adapters.market_prices import load_prices

@router.get("/health")
async def health_check():
    # Test weather adapter
    try:
        test_weather = get_forecast("Ahmedabad")
        weather_source = test_weather.get("source", "unknown")
    except Exception:
        weather_source = "error"
    
    # Test price adapter
    try:
        test_prices = load_prices("Cotton", "Ahmedabad APMC")
        price_source = "live" if len(test_prices) > 0 else "empty"
    except Exception:
        price_source = "error"
    
    return {
        "status": "OK",
        "version": "1.0.0-phase1",
        "adapters": {
            "weather": weather_source,
            "prices": price_source
        }
    }
```

### 7.2 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 7.1 | Update `/health` endpoint | Add `adapters` field with source status | Response includes `adapters.weather` and `adapters.prices` |
| 7.2 | Test health endpoint | Verify both adapters report correctly | `curl /health` shows source status |

---

## 8. Frontend — Data Source Indicator

**Dependencies:** 7 (health endpoint updated) | **Resources:** `Frontend/src/components/`

### 8.1 Purpose

Add a subtle, non-intrusive indicator on the dashboard showing whether the app is using live or mocked data. This is for evaluator transparency — judges can see the integration is real.

### 8.2 Component Design (`DataStatusIndicator.jsx`)

```jsx
import { useState, useEffect } from 'react'

export default function DataStatusIndicator() {
  const [status, setStatus] = useState(null)
  
  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setStatus(data.adapters))
      .catch(() => setStatus({ weather: 'unknown', prices: 'unknown' }))
  }, [])
  
  if (!status) return null
  
  const weatherColor = status.weather === 'live' ? 'text-emerald-600' : 'text-amber-600'
  const priceColor = status.prices === 'live' ? 'text-emerald-600' : 'text-amber-600'
  
  return (
    <div className="flex gap-3 text-xs">
      <span className={weatherColor}>
        Weather: {status.weather === 'live' ? '● Live API' : '○ Mock Data'}
      </span>
      <span className={priceColor}>
        Prices: {status.prices === 'live' ? '● Live API' : '○ Mock Data'}
      </span>
    </div>
  )
}
```

### 8.3 Placement

Add `<DataStatusIndicator />` to `Layout.jsx` footer or `Dashboard.jsx` header — a single line, not blocking any content.

### 8.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 8.1 | Create `DataStatusIndicator.jsx` | Component fetching `/api/health` | Component renders |
| 8.2 | Add to `Layout.jsx` footer | Non-intrusive placement | Indicator visible on all pages |
| 8.3 | Style with Tailwind | Green dot for live, amber for mock | Visual distinction clear |
| 8.4 | Test with live APIs | Both show "Live API" | Green dots visible |
| 8.5 | Test with fallback | Both show "Mock Data" | Amber dots visible |

---

## 9. Testing — Fallback Verification & Edge Cases

**Dependencies:** 4, 6, 8 (all adapters and fallbacks built) | **Resources:** Browser, curl

### 9.1 Weather Adapter Test Matrix

| Test Case | Setup | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Valid API key, network OK | Set real `OPENWEATHER_API_KEY` | Live forecast returned, `"source": "live"` | |
| Invalid API key | Set `OPENWEATHER_API_KEY=invalid` | Mock forecast returned, warning logged | |
| No API key | Unset `OPENWEATHER_API_KEY` | Mock forecast returned, warning logged | |
| Network timeout | Block API domain in hosts file | Mock forecast returned after 5s, warning logged | |
| All 5 locations | Test each location | Each returns valid 7-day forecast | |
| Response format | Compare live vs mock output | Same keys: `day`, `date`, `temp_high`, `temp_low`, `rain_chance`, `humidity`, `wind_kph` | |

### 9.2 Price Adapter Test Matrix

| Test Case | Setup | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Valid API key, network OK | Set real `AGMARKNET_API_KEY` | Live prices returned | |
| Invalid API key | Set `AGMARKNET_API_KEY=invalid` | CSV fallback used, warning logged | |
| No API key | Unset `AGMARKNET_API_KEY` | CSV fallback used, warning logged | |
| Network timeout | Block API domain | CSV fallback used after 5s, warning logged | |
| All 4 crops × 5 markets | Test each combination | 20 price series returned | |
| Decision engine output | Run `POST /post-harvest` for each crop/location | Same Sell/Store/Transport recommendations as Phase 0 | |

### 9.3 End-to-End Integration Tests

| Test | Steps | Expected |
|------|-------|----------|
| Full advisory flow | Enter crop, location, sowing date → submit | Advisory generated using live weather (or mock fallback) |
| Full post-harvest flow | Enter crop, quantity, storage, location → submit | Recommendation generated using live prices (or mock fallback) |
| Unified dashboard | Use quick preset → submit | Both modules return results, charts render |
| Fallback toggle | Set both API keys to invalid → run full flow | App works identically using mock data |
| Health endpoint | `GET /health` | Shows adapter source status |

### 9.4 Implementation Tasks

| # | Task | Description | Verification |
|---|------|-------------|-------------|
| 9.1 | Execute weather test matrix | All 5 locations, all failure modes | All tests pass |
| 9.2 | Execute price test matrix | All 4×5 combinations, all failure modes | All tests pass |
| 9.3 | Execute end-to-end integration tests | Full flows with live and mock | No regressions |
| 9.4 | Document test results | Write results in completion report | `chunk-5-completion-report.md` |

---

## 10. Deployment & Integration Verification

**Dependencies:** 9 (tests passed) | **Resources:** Vercel, Render

### 10.1 Environment Variables on Render

Set the following environment variables in the Render dashboard:

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENWEATHER_API_KEY` | Your free API key | From openweathermap.org |
| `AGMARKNET_API_KEY` | Your data.gov.in key | If available; otherwise leave blank for CSV fallback |

### 10.2 Deployment Steps

| # | Task | Command / Action | Verification |
|---|------|------------------|-------------|
| 10.1 | Add `httpx` to `requirements.txt` | `httpx>=0.27` | File updated |
| 10.2 | Commit all changes | `git add . && git commit -m "feat(phase1): live weather + price adapters with fallback"` | Clean commit |
| 10.3 | Push to GitHub | `git push origin main` | Render auto-deploys |
| 10.4 | Verify backend `/health` | `curl https://<render-url>/health` | Shows adapter source status |
| 10.5 | Verify frontend | Open Vercel URL | Data status indicator shows live/mock |
| 10.6 | Run full advisory flow | Submit a scenario | Advisory generated correctly |
| 10.7 | Run full post-harvest flow | Submit a scenario | Recommendation generated correctly |
| 10.8 | Test fallback on deployed app | Remove env vars on Render, redeploy | App falls back to mock data |

### 10.3 Verify Phase 0 Features Still Work

| Feature | Status | Notes |
|---------|--------|-------|
| `/health` returns OK | | |
| `/locations` returns 5 locations | | |
| `/crops` returns 4 crops | | |
| `/advisory` returns 3 ranked advisories | | |
| `/post-harvest` returns Sell/Store/Transport | | |
| `/rules` returns crop rules | | |
| Dashboard renders side-by-side | | |
| SpoilageChart renders | | |
| PriceTrendChart renders | | |
| Mobile layout works (375px) | | |

---

## 11. Done Criteria Checklist

To sign off on Chunk 5, all criteria must be checked and verified:

- [ ] `httpx` added to `requirements.txt` and installs cleanly
- [ ] `Backend/App/adapters/config.py` created with env var loader
- [ ] `Backend/App/adapters/weather.py` rewritten with live OpenWeatherMap + mock fallback
- [ ] `get_forecast()` returns same dict shape + `"source"` field
- [ ] Mock forecast logic preserved exactly from Phase 0
- [ ] `Backend/App/adapters/market_prices.py` created with live API + CSV fallback
- [ ] `load_prices()` tries live API first, falls back to CSV silently
- [ ] `get_latest_price()` and `get_future_price()` moved to adapter, same interface
- [ ] `decision.py` updated to import from adapter, no logic changes
- [ ] All fallback modes tested: invalid key, no key, network timeout, malformed response
- [ ] User NEVER sees an error screen — fallback is invisible
- [ ] Python logging captures fallback events for developer debugging
- [ ] `/health` endpoint returns adapter source status
- [ ] `DataStatusIndicator.jsx` created and showing live/mock status on frontend
- [ ] All 4×5 crop/location combinations tested end-to-end
- [ ] Decision engine output matches Phase 0 exactly (no regression)
- [ ] Environment variables set on Render deployment
- [ ] Deployed app verified: live data works when API keys present
- [ ] Deployed app verified: fallback works when API keys absent
- [ ] All Phase 0 features still functional (advisory, post-harvest, dashboard, charts)

---

## 12. Handoff to P2 Template

Create `Docs/handoff-to-p2-phase1.md` to guide Person 2 (Om B Patel) when starting Chunk 6 (Leaf-Disease Photo Classifier):

```markdown
# Handoff to Person 2 (Om B Patel) — Chunk 5 Completion & Chunk 6 Kickoff

Chunk 5 (Real Data Integrations) is 100% complete!

## Key Deliverables Added in Chunk 5:
- **Live Weather Adapter:** OpenWeatherMap API integration with silent fallback to deterministic mock.
- **Live Price Adapter:** Agmarknet/data.gov.in integration with silent fallback to `mandi_prices.csv`.
- **Data Status Indicator:** Frontend badge showing live/mock data source status.
- **Health Endpoint Enhanced:** `/health` now reports adapter source status.

## Starting Point for Chunk 6 (Leaf-Disease Photo Classifier):
1. `Frontend/src/components/AdvisoryForm.jsx` and `UnifiedScenarioForm.jsx`: The photo upload field exists but is currently unused — wire it to the new `/leaf-classify` endpoint.
2. `Backend/App/routers/`: Create new `POST /leaf-classify` endpoint.
3. `Backend/App/models/`: Add TFLite model loading logic.
4. Download PlantVillage dataset subset for 1–2 of the 4 crops (Cotton, Tomato recommended).

## Key Files to Know:
- `Backend/App/adapters/weather.py` — Live weather with fallback (DO NOT MODIFY)
- `Backend/App/adapters/market_prices.py` — Live prices with fallback (DO NOT MODIFY)
- `Frontend/src/components/DataStatusIndicator.jsx` — Status badge (can extend if needed)

All existing UI components, DB models, and rule files remain 100% intact!
```

---

## 13. Ponytail Simplification Log

| Pragmatic Choice / Shortcut | Skipped Mechanism | Reason & Future Resolution | File Location |
|-----------------------------|-------------------|----------------------------|---------------|
| `httpx` sync client | Async `httpx.AsyncClient` with event loop | Sync is simpler for demo; async needed when concurrency matters (Phase 2+) | `Backend/App/adapters/weather.py` |
| Environment variables for API keys | Vault, encrypted config, secrets manager | Sufficient for hackathon; Phase 2 moves to proper secrets management | `Backend/App/adapters/config.py` |
| 5-second timeout | Configurable retry logic with exponential backoff | One timeout is enough for demo; retry logic added in Phase 2 | `Backend/App/adapters/weather.py` |
| Health endpoint tests adapters | Dedicated adapter health-check endpoints | Single `/health` endpoint is enough for 2 adapters; split when more adapters appear | `Backend/App/routers/health.py` |
| `DataStatusIndicator` polls once on mount | WebSocket or SSE for real-time status | One-time check is enough for demo; real-time updates added if needed | `Frontend/src/components/DataStatusIndicator.jsx` |
| CSV fallback retained as-is | Auto-refreshing CSV via cron job | CSV is sufficient for demo; cron refresh added in Phase 2 pilot | `Backend/data/mandi_prices.csv` |
| No adapter retry logic | Circuit breaker pattern, retry with backoff | Not needed for hackathon demo; adds complexity without visible benefit | `Backend/App/adapters/` |

---

## 14. Resource Summary

| Software / Library | Version | Purpose | License |
|--------------------|---------|---------|---------|
| Python | 3.11+ / 3.13 | Backend runtime | PSF |
| FastAPI | 0.110+ | REST API framework | MIT |
| **httpx** | **0.27+ (NEW)** | **HTTP client for live API calls** | **BSD** |
| SQLAlchemy | 2.0+ | Database ORM | MIT |
| Pydantic | 2.x | Data validation | MIT |
| Node.js | 18+ | Frontend JS runtime | MIT |
| React | 18+ | UI component framework | MIT |
| Vite | 5+ | Frontend build tool | MIT |
| Tailwind CSS | 3.4+ | Utility-first CSS styling | MIT |
| Recharts | 2.12+ | Interactive SVG line charts | MIT |
| SQLite | 3.x | Embedded database | Public Domain |
| Uvicorn | 0.29+ | ASGI server | BSD |
| **OpenWeatherMap API** | **Free tier (NEW)** | **Live 7-day weather forecasts** | **Proprietary (free tier)** |
| **data.gov.in API** | **Free (NEW)** | **Live mandi price data** | **Open Government Data** |

---

## 15. Risk Register

| Risk Scenario | Likelihood | Impact | Applied Mitigation Strategy |
|---------------|------------|--------|-----------------------------|
| OpenWeatherMap rate limit hit during demo | Low | Medium | 60 calls/min free tier is more than enough; mock fallback handles overflow silently |
| data.gov.in API unreachable during demo | Medium | Medium | CSV fallback with 90 days of data; demo works identically without live prices |
| API keys accidentally committed to git | Low | High | Use `.env` file with `.gitignore`; never hardcode keys; Render env vars for deployment |
| Live weather data differs significantly from mock | Low | Low | Both produce same dict shape; advisory engine uses same logic regardless of source |
| httpx import fails on Render | Low | Medium | Add `httpx>=0.27` to `requirements.txt`; test with `pip install -r requirements.txt` locally first |
| Evaluator asks about data freshness | High | Low | Explain: live when available, mock as safety net; Phase 2 adds auto-refresh cron |
| Decision engine output changes with live prices | Low | Medium | Same algorithm, same interface; only the data source changes, not the computation |

---

## 16. Milestone Summary

| Milestone | Verification Gate |
|-----------|-------------------|
| **M1: Hackathon Brief Review** | Annotation list of requirement changes from pre-screening |
| **M2: Config Module Created** | `config.py` reads env vars correctly |
| **M3: Live Weather Adapter Working** | `get_forecast("Ahmedabad")` returns live data with valid API key |
| **M4: Weather Fallback Verified** | Invalid API key triggers mock fallback silently |
| **M5: Live Price Adapter Working** | `load_prices("Cotton", "Ahmedabad APMC")` returns live data |
| **M6: Price Fallback Verified** | Invalid API key triggers CSV fallback silently |
| **M7: Health Endpoint Updated** | `/health` returns adapter source status |
| **M8: Data Status Indicator Live** | Frontend shows live/mock status badge |
| **M9: End-to-End Tests Pass** | All 4×5 combinations work with both live and mock |
| **M10: Deployed & Verified** | Live app on Render + Vercel with adapter status confirmed |

---

*— End of Document —*
