# Software Requirements Document (SRD)

**Project:** AgriTech - Precision Crop Advisory & Post-Harvest Decision Engine  
**Version:** 1.0  
**Date:** July 2026  
**Team:** TetraTHON 2026  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Design Decisions](#3-design-decisions)
4. [Data Flow](#4-data-flow)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [Security Design](#7-security-design)
8. [Deployment Design](#8-deployment-design)
9. [Error Handling Strategy](#9-error-handling-strategy)
10. [Future Considerations](#10-future-considerations)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Document (SRD) describes the technical design and architecture of the AgriTech platform. It documents the rationale behind technology choices, system design, and implementation patterns.

### 1.2 Scope

This document covers:
- System architecture and component design
- Technology selection rationale
- Data flow and processing logic
- Database schema design
- API endpoint design
- Security and deployment architecture

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
graph TB
    User["Farmer"]
    
    subgraph Frontend["Frontend - React 18 + Tailwind CSS"]
        AdvisoryForm["Advisory Form"]
        PostHarvestForm["Post-Harvest Form"]
        Dashboard["Unified Dashboard"]
        Charts["Charts - Price Trends, Spoilage Curves"]
    end
    
    subgraph Backend["Backend - FastAPI REST API"]
        AdvisoryAPI["Advisory API"]
        PostHarvestAPI["Post-Harvest API"]
        MetadataAPI["Metadata API"]
        AdvisoryEngine["Advisory Engine"]
        DecisionEngine["Decision Engine"]
        SQLAlchemy["SQLAlchemy ORM"]
    end
    
    subgraph Data["Data Layer"]
        JSON[("JSON Rule Files")]
        CSV[("CSV Price Dataset")]
        SQLite[("SQLite Database")]
    end
    
    subgraph External["External APIs"]
        Weather["OpenWeatherMap"]
        Agmarknet["data.gov.in Agmarknet"]
    end
    
    User -->|"HTTPS"| Frontend
    Frontend -->|"POST /api/advisory"| AdvisoryAPI
    Frontend -->|"POST /api/post-harvest"| PostHarvestAPI
    Frontend -->|"GET /api/*"| MetadataAPI
    
    AdvisoryAPI --> AdvisoryEngine
    PostHarvestAPI --> DecisionEngine
    MetadataAPI --> SQLAlchemy
    
    AdvisoryEngine --> JSON
    AdvisoryEngine --> Weather
    DecisionEngine --> CSV
    SQLAlchemy --> SQLite
    
    Weather -->|"API call"| External
    Agmarknet -->|"API call"| External
```

### 2.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Frontend | User interface, form handling, chart rendering | React 18, Vite, Tailwind, Recharts |
| Backend API | Request routing, validation, response formatting | FastAPI, Pydantic |
| Advisory Engine | Growth stage calculation, rule matching, weather integration | Python, JSON rules |
| Decision Engine | Spoilage modeling, transport costing, financial comparison | Python, CSV data |
| Database | Session logging, metadata storage | SQLite, SQLAlchemy ORM |
| External APIs | Weather forecasts, market prices | OpenWeatherMap, data.gov.in |

---

## 3. Design Decisions

### 3.1 FastAPI Over Flask

| Criterion | FastAPI | Flask | Decision |
|-----------|---------|-------|----------|
| Async support | Native | Requires extensions | FastAPI |
| Auto-generated docs | Built-in (Swagger) | Manual | FastAPI |
| Request validation | Pydantic built-in | Manual | FastAPI |
| Performance | High (Starlette) | Medium | FastAPI |
| Learning curve | Medium | Low | Flask |

**Decision:** FastAPI chosen for built-in validation, async support, and auto-documentation. The 36-hour timeline makes these built-in features critical.

### 3.2 SQLite Over PostgreSQL

| Criterion | SQLite | PostgreSQL | Decision |
|-----------|--------|------------|----------|
| Setup time | Zero | Minutes | SQLite |
| Portability | Single file | Server required | SQLite |
| ACID compliance | Yes | Yes | Tie |
| Concurrent writes | Limited | Excellent | PostgreSQL |
| Scalability | Limited | Excellent | PostgreSQL |

**Decision:** SQLite chosen for zero-setup, portability, and crash safety. Acceptable for prototype scale (5 locations, 4 crops). Migration path to PostgreSQL is straightforward for production.

### 3.3 Tailwind CSS Over Component Libraries

| Criterion | Tailwind | MUI/Chakra | Decision |
|-----------|----------|------------|----------|
| Bundle size | ~3KB | ~200KB | Tailwind |
| Customization | Full control | Theme-based | Tailwind |
| Learning curve | Medium | Low | Tie |
| Design consistency | Manual | Built-in | MUI |

**Decision:** Tailwind chosen for minimal bundle size and full design control. With 14 components, custom styling is faster than learning and customizing a library.

### 3.4 State-Based Routing Over React Router

| Criterion | State Variable | React Router | Decision |
|-----------|---------------|--------------|----------|
| Setup time | Zero | Configuration | State |
| URL management | None | Deep linking | React Router |
| Bundle size | Zero | ~15KB | State |
| Complexity | Low | Medium | State |

**Decision:** State-based routing chosen for simplicity. Deep linking is unnecessary for a single-page hackathon demo.

### 3.5 Mock Fallback Strategy

**Problem:** External APIs (OpenWeatherMap, Agmarknet) may fail during demo.

**Solution:** Every external API call has a deterministic mock fallback:
- Weather: Location-specific mock forecasts
- Prices: CSV dataset with 1,800+ historical records

**Benefit:** Demo never fails. System works offline.

---

## 4. Data Flow

### 4.1 Crop Advisory Flow

```mermaid
flowchart TD
    A["User Input: location, crop, sowing_date, weather"] --> B["Validate Input (Pydantic)"]
    B -->|"Invalid"| B1["Return 400 Error"]
    B -->|"Valid"| C["Look Up Location & Crop (SQLite)"]
    C -->|"Not Found"| C1["Return 404 Error"]
    C -->|"Found"| D["Calculate Days Since Sowing"]
    D --> E["Determine Growth Stage (JSON rules)"]
    E --> F["Load Stage Rules"]
    F --> G["Fetch Weather Forecast"]
    G -->|"API Success"| G1["Use Live Data"]
    G -->|"API Failure"| G2["Use Mock Fallback"]
    G1 --> H["Apply Weather Risk Multipliers"]
    G2 --> H
    H --> I["Score Confidence Levels"]
    I --> J["Generate 3 Advisories"]
    J --> K["Log Session to Database"]
    K --> L["Return Response"]
```

### 4.2 Post-Harvest Decision Flow

```mermaid
flowchart TD
    A["User Input: crop, quantity, storage, location"] --> B["Validate Input (Pydantic)"]
    B -->|"Invalid"| B1["Return 400 Error"]
    B -->|"Valid"| C["Look Up Location & Crop (SQLite)"]
    C -->|"Not Found"| C1["Return 404 Error"]
    C -->|"Found"| D["Find Nearest Market (Haversine)"]
    D --> E["Calculate Transport Costs (5 markets)"]
    E --> F["Load Market Prices"]
    F -->|"API Success"| F1["Use Live Data"]
    F -->|"API Failure"| F2["Use CSV Fallback"]
    F1 --> G["Calculate Option 1: Sell Now"]
    F2 --> G
    G --> H["Calculate Option 2: Store 14 Days"]
    H --> I["Calculate Option 3: Transport to Best Market"]
    I --> J["Compare Net Returns"]
    J --> K["Select Optimal Recommendation"]
    K --> L["Log Session to Database"]
    L --> M["Return Response"]
```

### 4.3 Unified Dashboard Flow

```mermaid
flowchart LR
    A["Unified Form"] --> B["Promise.all()"]
    B --> C["POST /api/advisory"]
    B --> D["POST /api/post-harvest"]
    C --> E["Advisory Result"]
    D --> F["Post-Harvest Result"]
    E --> G["Side-by-Side Dashboard"]
    F --> G
    G --> H["Interactive Charts"]
```

---

## 5. Database Design

### 5.1 Entity Relationship Diagram

```mermaid
erDiagram
    locations {
        int id PK
        string name UK
        string state
        float latitude
        float longitude
    }
    
    crops {
        int id PK
        string name UK
        string category
        int typical_duration_days
    }
    
    farmer_sessions {
        int id PK
        int location_id FK
        int crop_id FK
        datetime sowing_date
        string weather_observation
        datetime created_at
    }
    
    post_harvest_sessions {
        int id PK
        int location_id FK
        int crop_id FK
        float quantity_quintals
        string storage_condition
        string recommendation
        float expected_return
        datetime created_at
    }
    
    locations ||--o{ farmer_sessions : "has"
    crops ||--o{ farmer_sessions : "has"
    locations ||--o{ post_harvest_sessions : "has"
    crops ||--o{ post_harvest_sessions : "has"
```

### 5.2 Table Definitions

#### locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR | UNIQUE, NOT NULL | City name |
| state | VARCHAR | NOT NULL | State name |
| latitude | FLOAT | NOT NULL | Geographic latitude |
| longitude | FLOAT | NOT NULL | Geographic longitude |

#### crops

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR | UNIQUE, NOT NULL | Crop name |
| category | VARCHAR | NOT NULL | cash_crop / cereal / vegetable |
| typical_duration_days | INTEGER | NOT NULL | Growth period in days |

#### farmer_sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| location_id | INTEGER | FK → locations.id | Requested location |
| crop_id | INTEGER | FK → crops.id | Requested crop |
| sowing_date | DATETIME | NULLABLE | Farmer-provided date |
| weather_observation | VARCHAR | NULLABLE | Weather condition |
| created_at | DATETIME | DEFAULT NOW() | Request timestamp |

#### post_harvest_sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| location_id | INTEGER | FK → locations.id | Requested location |
| crop_id | INTEGER | FK → crops.id | Requested crop |
| quantity_quintals | FLOAT | NOT NULL | Quantity input |
| storage_condition | VARCHAR | NOT NULL | Storage type |
| recommendation | VARCHAR | NOT NULL | System recommendation |
| expected_return | FLOAT | NOT NULL | Expected net return |
| created_at | DATETIME | DEFAULT NOW() | Request timestamp |

---

## 6. API Design

### 6.1 Endpoint Overview

| Method | Endpoint | Purpose | Rate Limit |
|--------|----------|---------|------------|
| GET | /api/health | System health check | Unlimited |
| GET | /api/locations | List available locations | Unlimited |
| GET | /api/crops | List supported crops | Unlimited |
| GET | /api/rules | Get merged crop rules | Unlimited |
| POST | /api/advisory | Generate crop advisories | 30/min |
| POST | /api/post-harvest | Generate post-harvest plan | 30/min |
| GET | /api/price-history | Get price trend data | 30/min |
| GET | /api/spoilage-curve | Get spoilage projection | 30/min |
| POST | /api/leaf-classify | Classify leaf image | 30/min |

### 6.2 Request/Response Patterns

```mermaid
flowchart LR
    subgraph POST["POST Endpoint Pattern"]
        A1["Request"] --> B1["Pydantic Validation"]
        B1 -->|"Invalid"| C1["HTTPException (400/404)"]
        B1 -->|"Valid"| D1["Business Logic"]
        D1 --> E1["Database Log"]
        E1 --> F1["Response"]
    end
    
    subgraph GET["GET Endpoint Pattern"]
        A2["Request"] --> B2["Check Cache"]
        B2 -->|"Cache Hit"| C2["Return Cached"]
        B2 -->|"Cache Miss"| D2["Fetch Data"]
        D2 --> E2["Update Cache"]
        E2 --> F2["Return Data"]
    end
```

### 6.3 Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad request (validation failed) |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## 7. Security Design

### 7.1 Rate Limiting

| Implementation | slowapi middleware |
|----------------|-------------------|
| Limit | 30 requests/minute per endpoint |
| Scope | Per IP address |
| Response | 429 Too Many Requests |

### 7.2 CORS Configuration

```python
origins = ["http://localhost:5173"]  # Development
# Production: specific domain from environment variable
```

### 7.3 Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | XSS protection |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer |

### 7.4 Input Validation

- All inputs validated via Pydantic schemas
- SQL injection prevented by SQLAlchemy ORM
- File uploads validated by type and size

---

## 8. Deployment Design

### 8.1 Deployment Architecture

```mermaid
flowchart TB
    subgraph GitHub["GitHub Repository"]
        Code["Source Code"]
        Actions["GitHub Actions CI"]
    end
    
    subgraph Render["Render (Backend)"]
        Pull1["Pull from GitHub"]
        Install1["Install Dependencies"]
        Migrate["Run Migrations"]
        Server["Start Server"]
    end
    
    subgraph Vercel["Vercel (Frontend)"]
        Pull2["Pull from GitHub"]
        Build["npm run build"]
        CDN["Deploy to CDN"]
    end
    
    Code --> Actions
    Actions --> Pull1
    Actions --> Pull2
    Pull1 --> Install1
    Install1 --> Migrate
    Migrate --> Server
    Pull2 --> Build
    Build --> CDN
```

### 8.2 Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| AUTO_SEED | Auto-populate database | Yes |
| OPENWEATHER_API_KEY | Weather API access | No (mock fallback) |
| AGMARKNET_API_KEY | Market price API access | No (CSV fallback) |
| CORS_ORIGINS | Allowed frontend domains | Yes |

### 8.3 Build Commands

**Backend:**
```bash
pip install -r requirements.txt
uvicorn App.main:app --host 0.0.0.0 --port $PORT
```

**Frontend:**
```bash
npm install
npm run build
```

---

## 9. Error Handling Strategy

### 9.1 Error Categories

| Category | Example | Handling |
|----------|---------|----------|
| Validation Error | Invalid date format | 400 + descriptive message |
| Not Found | Unknown crop name | 404 + resource name |
| External API Failure | Weather API timeout | Mock fallback |
| Business Logic Error | Zero quantity | 400 + validation message |
| System Error | Database connection | 500 + logged error |

### 9.2 Fallback Chain

```mermaid
flowchart TD
    A["External API Call"] --> B{"Success?"}
    B -->|"Yes"| C["Return Live Data"]
    B -->|"No"| D{"Cache Hit?"}
    D -->|"Yes"| E["Return Cached Data"]
    D -->|"No"| F["Return Mock Data"]
```

### 9.3 Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
```

---

## 10. Future Considerations

### 10.1 Scalability Path

```mermaid
flowchart LR
    A["Phase 1: Add Crops"] --> B["Phase 2: Add Locations"]
    B --> C["Phase 3: PostgreSQL"]
    C --> D["Phase 4: Auth"]
    D --> E["Phase 5: Mobile App"]
```

| Phase | Change | Effort |
|-------|--------|--------|
| Phase 1 | Add more crops (10+) | Data addition |
| Phase 2 | Add more locations (50+) | Data addition |
| Phase 3 | PostgreSQL migration | Connection string change |
| Phase 4 | User authentication | Add auth middleware |
| Phase 5 | Mobile app (React Native) | Reuse API layer |

### 10.2 Technical Debt

| Item | Priority | Effort |
|------|----------|--------|
| Add database migrations (Alembic) | High | 2 hours |
| Add structured logging | Medium | 2 hours |
| Add API versioning (/v1/) | Low | 1 hour |
| Add TypeScript to frontend | Low | 8 hours |
| Add E2E tests | Medium | 4 hours |

### 10.3 Potential Enhancements

| Enhancement | Value |
|-------------|-------|
| Multi-language support (Hindi, Gujarati) | Wider reach |
| SMS advisory delivery | Offline access |
| Offline mode (PWA) | No internet required |
| Machine learning yield prediction | Higher accuracy |
| Satellite imagery integration | Remote sensing |

---

*- AgriTech SRD v1.0 -*
