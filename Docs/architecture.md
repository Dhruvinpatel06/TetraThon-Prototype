# AgriTech — System Architecture (Phase 0)

AgriTech is designed as a decoupled, high-performance client-server web application. The frontend is a single-page React 18 application with interactive Recharts visualizations, and the backend is a lightweight FastAPI REST API backed by SQLite, JSON agronomic rules, and decision engines.

---

## Architecture Diagram

```mermaid
flowchart TD
    subgraph Client ["Frontend (React 18 + Vite 5 + Recharts)"]
        UI["App.jsx (View Router)"]
        FormA["AdvisoryForm.jsx"]
        FormB["PostHarvestForm.jsx"]
        FormU["UnifiedScenarioForm.jsx"]
        Dash["Dashboard.jsx (Side-by-Side View)"]
        ChartSpoil["SpoilageChart.jsx (30-Day Curve)"]
        ChartTrend["PriceTrendChart.jsx (90-Day Trend)"]
    end

    subgraph Server ["Backend (FastAPI REST API)"]
        Main["App/main.py"]
        AdvRouter["App/routers/advisory.py"]
        PHRouter["App/routers/post_harvest.py"]
        MetaRouters["App/routers/locations.py, crops.py, health.py"]

        AdvEngine["App/engine/advisory.py"]
        DecEngine["App/engine/decision.py"]
        SpoilageModel["App/engine/spoilage.py"]
        TransModel["App/engine/transport.py"]
        WeatherAdapter["App/adapters/weather.py"]
    end

    subgraph Data ["Data Layer"]
        DB[(SQLite Session DB)]
        CSV[(data/mandi_prices.csv - 1800 rows)]
        Rules[(data/*_rules.json - Irrigation, Fertiliser, Pest)]
    end

    UI --> FormA
    UI --> FormB
    UI --> FormU
    UI --> Dash

    Dash --> ChartSpoil
    Dash --> ChartTrend

    FormU -->|Promise.all() concurrent POST| AdvRouter
    FormU -->|Promise.all() concurrent POST| PHRouter

    AdvRouter --> AdvEngine
    PHRouter --> DecEngine

    AdvEngine --> WeatherAdapter
    AdvEngine --> Rules

    DecEngine --> SpoilageModel
    DecEngine --> TransModel
    DecEngine --> CSV

    MetaRouters --> DB
```

---

## Detailed Component Breakdown

### 1. Frontend (React 18 + Vite 5 + Tailwind CSS 3.4 + Recharts 2.12)
* **View Routing Engine:** Lightweight state-based view router (`home` | `form` | `results` | `ph-form` | `ph-results` | `dashboard-form` | `dashboard`) eliminating client-side router overhead.
* **Unified Intelligence Form (`UnifiedScenarioForm.jsx`):** Single intake interface triggering dual `Promise.all()` concurrent requests to `/advisory` and `/post-harvest` endpoints. Features 4 quick evaluation presets.
* **Side-by-Side Dashboard (`Dashboard.jsx`):** 2-column grid layout displaying Module A stage advisories and Module B financial recommendations concurrently.
* **Interactive Charts (`SpoilageChart.jsx` & `PriceTrendChart.jsx`):** Client-side SVG line chart renderers powered by Recharts for 30-day produce decay curves and 90-day mandi price trends.

### 2. Backend (FastAPI Framework)
* **Endpoints:**
  * `GET /health`: Health status.
  * `GET /locations`: Retrieves seeded Gujarat locations.
  * `GET /crops`: Retrieves configured crops.
  * `GET /rules`: Returns merged crop stages rules.
  * `POST /advisory`: Processes farmer session data through advisory ranking engine.
  * `POST /post-harvest`: Calculates Sell Now vs Store vs Transport financial decision.
* **Middleware:** Wide-open CORS middleware enabling seamless cross-origin request handling.

### 3. Database (SQLite + SQLAlchemy 2.0 ORM)
* **Models (`Backend/App/models.py`):**
  * `Location`: ID, name, state, latitude, longitude.
  * `Crop`: ID, name, category, typical duration (days).
  * `FarmerSession`: Logged advisory requests.
  * `PostHarvestSession`: Logged post-harvest planning requests.

### 4. Decision Engines & Adapters
* **Advisory Engine (`App/engine/advisory.py`):** Calculates crop age from sowing date, matches growth stage, applies weather risk multipliers, and ranks top 3 advisories with confidence scores.
* **Spoilage Model (`App/engine/spoilage.py`):** Calculates daily produce decay rates based on storage type (Open, Warehouse, Cold Storage) and crop sensitivity modifiers.
* **Transport Cost Model (`App/engine/transport.py`):** Computes Haversine straight-line distances between farm location and APMC markets with transport pricing (₹5/km/q, ₹500 min).
* **Decision Engine (`App/engine/decision.py`):** Reads 1,800-row mandi price dataset and compares net financial realizations to identify the optimal strategy.

---
*— Updated for Phase 0 Submission —*
