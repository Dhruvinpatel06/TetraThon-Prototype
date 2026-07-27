# API Documentation

Base URL: `https://agritech-backend.onrender.com/api`

All endpoints accept and return JSON. Rate limit: 30 requests/minute per endpoint.

---

## Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "adapters": {
    "weather": "mock",
    "market_prices": "mock"
  }
}
```

---

## Locations

```
GET /api/locations
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ahmedabad",
    "state": "Gujarat",
    "latitude": 23.0225,
    "longitude": 72.5714
  }
]
```

---

## Crops

```
GET /api/crops
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Cotton",
    "typical_duration_days": 180,
    "category": "cash_crop"
  }
]
```

---

## Rules

```
GET /api/rules
```

**Response:**
```json
{
  "irrigation": { "Cotton": [...] },
  "fertiliser": { "Cotton": [...] },
  "pest": { "Cotton": [...] }
}
```

---

## Crop Advisory

```
POST /api/advisory
```

**Request Body:**
```json
{
  "location_name": "Ahmedabad",
  "crop_name": "Cotton",
  "sowing_date": "2026-06-15",
  "weather_observation": "hot_and_dry"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location_name` | string | Yes | Must match a seeded location name |
| `crop_name` | string | Yes | Must match a seeded crop name |
| `sowing_date` | string | Yes | Format: `YYYY-MM-DD` |
| `weather_observation` | string | No | One of: `hot_and_dry`, `humid_cloudy`, `light_rain`, `heavy_rain` |

**Response (200):**
```json
{
  "advisories": [
    {
      "type": "irrigation",
      "title": "Irrigation Advisory",
      "confidence": "High",
      "plain_text": "Your Cotton is in the Flowering Boll stage. Apply 10.0cm of water every 2 day(s). No significant rain expected.",
      "details": {
        "stage": "Flowering Boll",
        "day_range": [90, 150],
        "interval_days": 2,
        "water_cm": 10.0,
        "is_generic_fallback": false
      }
    },
    {
      "type": "fertiliser",
      "title": "Fertiliser Advisory",
      "confidence": "High",
      "plain_text": "Your Cotton is in the Flowering Boll stage. Apply 40kg Nitrogen, 20kg Phosphorus, 20kg Potassium per acre.",
      "details": {
        "stage": "Flowering Boll",
        "day_range": [90, 150],
        "npk_kg_per_acre": { "N": 40, "P": 20, "K": 20 },
        "note": "Top-dress split into 2 applications.",
        "is_generic_fallback": false
      }
    },
    {
      "type": "pest",
      "title": "Pest Advisory",
      "confidence": "Medium",
      "plain_text": "Your Cotton is in the Flowering Boll stage. Watch for Bollworm (Risk: Medium). Monitor crop regularly.",
      "details": {
        "stage": "Flowering Boll",
        "day_range": [90, 150],
        "pest_or_disease": "Bollworm",
        "default_risk": "Medium",
        "calculated_risk": "Medium",
        "is_generic_fallback": false
      }
    }
  ],
  "session_id": 1
}
```

**Error Responses:**
| Status | Meaning |
|--------|---------|
| `400` | Empty fields or invalid date format |
| `404` | Location or crop not found |
| `500` | Engine failure |

---

## Post-Harvest Planner

```
POST /api/post-harvest
```

**Request Body:**
```json
{
  "crop_name": "Cotton",
  "quantity_quintals": 50.0,
  "storage_condition": "warehouse",
  "location_name": "Ahmedabad"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `crop_name` | string | Yes | Must match a seeded crop name |
| `quantity_quintals` | float | Yes | Must be > 0 |
| `storage_condition` | string | Yes | One of: `open`, `warehouse`, `cold_storage` |
| `location_name` | string | Yes | Must match a seeded location name |

**Response (200):**
```json
{
  "recommendation": "transport",
  "option_label": "Transport to Best Market",
  "expected_return": 312500.0,
  "expected_return_per_quintal": 6250.0,
  "details": {
    "sell_now": {
      "market": "Ahmedabad APMC",
      "price_per_quintal": 6200.0,
      "transport_cost": 1250.0,
      "net_return": 308750.0,
      "distance_km": 15.0
    },
    "store": {
      "market": "Ahmedabad APMC",
      "store_days": 14,
      "storage": "warehouse",
      "spoilage_loss": 4960.0,
      "storage_cost": 1400.0,
      "future_price_per_quintal": 6400.0,
      "net_return": 303640.0
    },
    "transport": {
      "market": "Surat APMC",
      "price_per_quintal": 6500.0,
      "transport_cost": 3750.0,
      "distance_km": 45.0,
      "net_return": 321250.0
    }
  },
  "reason": "Transporting to Surat APMC yields an expected return of ₹321,250 — ₹12,500 more than selling locally.",
  "session_id": 1
}
```

**Recommendation Types:**
| Value | Meaning |
|-------|---------|
| `sell_now` | Sell at nearest market immediately |
| `store` | Store for 14 days, then sell |
| `transport` | Transport to a more profitable market |
| `hold_consult` | All options yield net loss — consult advisor |

---

## Price History

```
GET /api/price-history?crop=Cotton&location=Ahmedabad
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `crop` | string | `Cotton` | Crop name |
| `location` | string | `Ahmedabad` | Location name |

**Response (200):**
```json
{
  "crop": "Cotton",
  "location": "Ahmedabad",
  "history": [
    {
      "date": "2026-01-15",
      "Ahmedabad APMC": 6100.0,
      "Surat APMC": 6300.0,
      "Vadodara APMC": 6150.0,
      "Rajkot APMC": 6050.0,
      "Anand APMC": 6200.0
    }
  ]
}
```

---

## Spoilage Curve

```
GET /api/spoilage-curve?crop=Cotton&quantity=50
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `crop` | string | `Cotton` | Crop name |
| `quantity` | float | `10.0` | Quantity in quintals |

**Response (200):**
```json
{
  "crop": "Cotton",
  "quantity": 50.0,
  "curve": [
    {
      "day": "Day 0",
      "open": 310000,
      "warehouse": 310000,
      "cold_storage": 310000
    },
    {
      "day": "Day 1",
      "open": 303800,
      "warehouse": 306900,
      "cold_storage": 308550
    }
  ]
}
```

---

## Leaf Classification

```
POST /api/leaf-classify
```

**Request:** `multipart/form-data` with `file` field containing an image.

**Response (200):**
```json
{
  "prediction": "Healthy",
  "confidence": 0.92
}
```

---

*— Phase 0 Submission —*
