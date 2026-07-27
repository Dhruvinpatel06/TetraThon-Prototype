# AgriTech — System Architecture

A dual-engine agricultural decision support system combining crop growth advisories with post-harvest loss minimization.

---

## High-Level Architecture

```mermaid
flowchart TD
    Farmer["👨‍🌾 Farmer"]

    subgraph Frontend ["Frontend — React 18 + Tailwind CSS"]
        WebApp["Single-Page App"]
        AdvisoryUI["Crop Advisory Form"]
        PostHarvestUI["Post-Harvest Form"]
        Dashboard["Unified Dashboard"]
        Charts["Charts — Price Trends, Spoilage Curves"]
    end

    subgraph Backend ["Backend — FastAPI REST API"]
        API["REST Endpoints"]
        AdvisoryEngine["Advisory Engine"]
        DecisionEngine["Decision Engine"]
        SpoilageModel["Spoilage Model"]
        TransportModel["Transport Model"]
    end

    subgraph Data ["Data Layer"]
        DB[("SQLite Database")]
        Rules["JSON Rule Files — Irrigation, Fertiliser, Pest"]
        MandiCSV["Mandi Price Dataset — 1800 rows"]
    end

    subgraph External ["External APIs"]
        Weather["OpenWeatherMap API"]
    end

    Farmer --> WebApp
    WebApp --> AdvisoryUI
    WebApp --> PostHarvestUI
    WebApp --> Dashboard
    Dashboard --> Charts

    AdvisoryUI -->|POST /api/advisory| API
    PostHarvestUI -->|POST /api/post-harvest| API
    Dashboard -->|Promise.all — concurrent| API

    API --> AdvisoryEngine
    API --> DecisionEngine

    AdvisoryEngine --> Rules
    AdvisoryEngine --> Weather
    AdvisoryEngine --> DB

    DecisionEngine --> SpoilageModel
    DecisionEngine --> TransportModel
    DecisionEngine --> MandiCSV
    DecisionEngine --> DB

    style Farmer fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style Frontend fill:#ecfdf5,stroke:#059669
    style Backend fill:#f0f9ff,stroke:#0284c7
    style Data fill:#fefce8,stroke:#ca8a04
    style External fill:#fdf2f8,stroke:#db2777
```

---

## Component Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Vite 5, Tailwind CSS, Recharts | Single-page UI with forms, dashboard, charts |
| **Backend** | FastAPI, Pydantic, SQLAlchemy 2.0 | REST API with validation and ORM |
| **Database** | SQLite | Session logging, location/crop metadata |
| **Rule Engine** | JSON files + Python logic | Crop-stage advisory generation |
| **Decision Engine** | Python + CSV data | Post-harvest profit optimization |
| **External** | OpenWeatherMap | Live weather data for risk multipliers |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check |
| `GET` | `/api/locations` | Available farm locations |
| `GET` | `/api/crops` | Supported crop profiles |
| `GET` | `/api/rules` | Merged crop stage rules |
| `POST` | `/api/advisory` | Generate crop advisories |
| `POST` | `/api/post-harvest` | Generate post-harvest plan |
| `POST` | `/api/leaf-classify` | Classify leaf disease from image |

---

*— Phase 0 Submission —*
