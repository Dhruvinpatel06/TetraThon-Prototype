# AgriTech — Pre-Screening Pitch Deck (TetraTHON 2026)

> **Precision Agriculture & Post-Harvest Decision Intelligence Engine**

---

## Slide 1: Title & Project Overview

### **AgriTech**
*Empowering Smallholder Farmers with Dual-Engine Advisory & Post-Harvest Financial Optimization*

* **Event:** TetraTHON 2026 Hackathon
* **Track:** Precision Agriculture & AgriTech Innovation
* **Phase:** Phase 0 Pre-Screening Prototype Submission
* **Team:** Om B Patel, Mithil Desai, Dhruvin Patel, Saumya

---

## Slide 2: Problem Understanding

### **Challenges Facing Gujarat Smallholder Farmers**

1. **Severe Post-Harvest Losses (15%–25% Produce Waste):**
   * Farmers lack data-driven decision tools for timing sales, calculating spoilage decay across storage types, or evaluating transport costs.
2. **Suboptimal In-Season Resource Timing (20%–30% Yield Penalty):**
   * Generic farming advice ignores crop growth stages and local 7-day weather forecasts, leading to over-watering or misplaced fertilizer applications.
3. **Mandi Price Asymmetry:**
   * Farmers sell at the nearest APMC without visibility into price divergence across neighboring regional markets.

---

## Slide 3: Proposed Dual-Engine Approach

### **Unified Precision Intelligence Engine**

```
                     ┌────────────────────────────────┐
                     │        AgriTech Engine         │
                     └───────────────┬────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│     Module A: Crop Advisory     │             │    Module B: Post-Harvest     │
│  - Crop Stage Identification    │             │  - 30-Day Spoilage Decay Curves │
│  - Weather-Aware Rule Engine    │             │  - Haversine Distance Transport │
│  - Ranked Irrigation/NPK/Pest   │             │  - APMC Mandi Price Decision    │
└─────────────────────────────────┘             └─────────────────────────────────┘
```

* **Module A (In-Season Precision Advisory):** Generates stage-specific irrigation (water depth & interval), NPK fertilizer dosages, and pest risk alerts based on 7-day weather observations.
* **Module B (Post-Harvest Loss Planner):** Calculates net expected financial returns comparing **Sell Now**, **Store (14 Days)**, and **Transport to Best Market** options.

---

## Slide 4: Technical Architecture

### **Clean, Decoupled & Lightweight Stack**

* **Frontend:** React 18, Vite 5, Tailwind CSS 3.4, Recharts (Interactive SVG line charts).
* **Backend:** FastAPI (Python 3.11+), Uvicorn ASGI server, Pydantic v2 schemas.
* **Data Layer:** SQLite embedded ORM database (`Location`, `Crop`, `FarmerSession`, `PostHarvestSession`), 1,800-row APMC Mandi price dataset (`mandi_prices.csv`).
* **Rule Engine:** JSON-based stage and weather rule matrices for Cotton, Wheat, Groundnut, and Tomato across 5 Gujarat APMCs (Ahmedabad, Surat, Vadodara, Rajkot, Anand).

---

## Slide 5: Live Product & Interactive Dashboard

### **Unified Side-by-Side Intelligence Dashboard**

* **Single-Intake Scenario Form:** Select Location, Crop, Sowing Date, Weather, Quantity (quintals), and Storage Condition with **4 Quick Demo Presets**.
* **Dual Parallel Execution:** `Promise.all()` concurrent API queries render Module A and Module B recommendations simultaneously.
* **Interactive Recharts Visualizations:**
  * *Spoilage Decay Chart:* 30-day value retention curves comparing Open Field, Covered Warehouse, and Cold Storage.
  * *Price Trend Chart:* 90-day historical APMC mandi prices illustrating market arbitrage opportunities.

---

## Slide 6: Market Fit & Financial Impact

### **Quantifiable ROI for Farmers**

| Crop Scenario | Baseline Sell Now | Recommended Strategy | Net Financial Gain |
|---------------|-------------------|----------------------|--------------------+
| **Cotton (Anand, 10q)** | ₹62,000 | Transport to Surat APMC | **+₹1,862 net gain** |
| **Wheat (Ahmedabad, 25q)** | ₹60,000 | Store 14 Days Cold Storage | **+₹3,250 net gain** |
| **Tomato (Surat, 15q)** | ₹29,250 | Sell Now (Prevent Spoilage) | **Avoids ₹8,500 loss** |

* **Distribution Model:** Low-bandwidth client web app deployable via Farmer Producer Organizations (FPOs) & Krishi Vigyan Kendras (KVKs).

---

## Slide 7: Scalability & Hackathon Roadmap

### **4-Phase Product Evolution**

1. **Phase 0 — Prototype (CURRENT):** Deterministic weather adapter, synthetic 90-day mandi CSV engine, rule-based inference, side-by-side Recharts dashboard.
2. **Phase 1 — Hackathon MVP (Week 2):** Live OpenWeatherMap API & Agmarknet/data.gov.in price API integration with silent fallback; client TFLite leaf image classifier.
3. **Phase 2 — Pilot Rollout:** WhatsApp Bot integration (Twilio/Gupshup) & multi-tenant FPO agent portals.
4. **Phase 3 — Enterprise Scale:** Cloud microservices on Kubernetes + automated ML model retraining pipelines.

---
*— End of Pitch Deck Presentation —*
