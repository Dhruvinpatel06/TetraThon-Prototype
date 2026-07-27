# Tech Stack Justification

Every tool in this project was chosen for a specific reason. No framework was added because "it's popular" — each solves a concrete problem.

---

## Frontend

| Tool | Version | Why It Was Chosen |
|------|---------|-------------------|
| **React** | 18.3 | Component-based UI with hooks. Team already knows it. Huge ecosystem. |
| **Vite** | 5.4 | 10x faster than CRA. HMR in milliseconds. Zero config. |
| **Tailwind CSS** | 3.4 | Utility-first CSS. No component library needed — we build our own simple components. Faster than writing custom CSS. |
| **Recharts** | 3.10 | Declarative charting built on D3. Simple API for line charts (price trends, spoilage curves). No need for Chart.js or Plotly. |

### Why not Next.js?
We don't need SSR, routing, or server components. A single-page app with state-based routing is simpler and faster for a hackathon prototype.

### Why not a component library (MUI, Chakra)?
Adds 200KB+ to bundle. We have 14 components — writing them with Tailwind is faster than learning and customizing a library.

---

## Backend

| Tool | Version | Why It Was Chosen |
|------|---------|-------------------|
| **FastAPI** | 0.139 | Async-ready, auto-generates OpenAPI docs, Pydantic validation built-in. 5x faster than Flask for I/O-bound work. |
| **SQLAlchemy** | 2.0 | ORM with type hints. Session management, migrations, and relationship mapping without raw SQL. |
| **SQLite** | Built-in | Zero setup, single file, ACID-compliant. Perfect for prototype. Can migrate to PostgreSQL later. |
| **Pydantic** | 2.13 | Request/response validation at the boundary. Catches bad data before it hits the engine. |
| **httpx** | 0.27 | Async HTTP client for weather and market API calls. Better than `requests` for timeout handling. |
| **SlowAPI** | 0.1.9 | Rate limiting middleware. Prevents API abuse during demo. |

### Why not Flask?
Flask lacks async support, auto-docs, and built-in validation. FastAPI gives us all three with less boilerplate.

### Why not PostgreSQL?
SQLite is zero-config and portable. We can demo on any machine without installing a database server. If this scales to production, PostgreSQL is a one-line connection string change.

---

## Data Layer

| Component | Why |
|-----------|-----|
| **JSON rule files** | Agronomic rules change per crop/stage. JSON is human-readable, version-controllable, and doesn't need a database migration. |
| **CSV price dataset** | 1,800 rows of historical mandi prices. CSV is the standard format for government agricultural data. |
| **SQLite sessions** | Logs every farmer request for auditing. Lightweight, no separate server. |

---

## External APIs

| API | Why |
|-----|-----|
| **OpenWeatherMap** | Free tier provides 7-day forecasts. Essential for weather-aware irrigation advice. |
| **data.gov.in (Agmarknet)** | Government mandi price data. Authoritative source for Indian agricultural market prices. |

### Fallback Strategy
Both external APIs have **mock fallbacks**. If the API is down or the key is missing, the app still works with deterministic mock data. This ensures the demo never fails.

---

## DevOps

| Tool | Why |
|------|-----|
| **Render** | Free tier hosting for backend. Auto-deploys from GitHub. |
| **Vercel** | Free tier hosting for frontend. Instant deploys, CDN included. |
| **GitHub Actions** | CI/CD pipeline for testing and deployment. |

---

## What We Rejected

| Tool | Why Not |
|------|---------|
| **Docker** | Adds complexity for a prototype. Not needed for 4-person team. |
| **Redis** | Overkill for caching. In-memory dict with TTL is sufficient. |
| **Celery** | No background tasks that need a task queue. |
| **GraphQL** | REST is simpler for our 6 endpoints. GraphQL adds schema complexity. |
| **TypeScript** | Team knows JSX well. TypeScript adds compilation step and type definitions. |

---

*— Phase 0 Submission —*
