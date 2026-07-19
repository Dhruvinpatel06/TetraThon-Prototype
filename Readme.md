# ArgiTech — Precision Crop Advisory & Post-Harvest Planner

An integrated platform for smallholder farmers: personalised crop advisories and post-harvest decision support, built for the ArgiTech pre-screening round.

## Problem

India's 85%+ smallholder farmers lack personalised agronomic advice, and 15–20% of produce is lost post-harvest due to poor storage and market-timing decisions. This prototype addresses both gaps with a single, demoable web application.

## Features

- **Crop Advisory Engine** — Enter location, crop, and sowing date → get 3 ranked advisories (irrigation, fertiliser, pest/disease) with confidence scores and plain-language explanations
- **Post-Harvest Planner** — Enter crop, quantity, storage condition → get Sell / Store / Transport recommendation with expected-return estimate, spoilage curves, and price trends
- **4 crop types** × **5 locations** covered end-to-end
- Mocked weather and market-price data — live API swap without UI changes

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS 3 |
| Backend | Python 3.11+, FastAPI, SQLAlchemy, SQLite |
| Charts | Recharts |
| Hosting | TBD |

## Architecture

```mermaid
flowchart LR
    A[Frontend<br/>React + Tailwind] --> B[FastAPI Backend]
    B --> C[(SQLite)]
    B --> D[Rule Engine<br/>JSON Tables]
    B --> E[Weather Adapter<br/>Mocked JSON]
    B --> F[Coming Soon<br/>Mandi Price, Spoilage, Transport]
    A -.-> I[Deploy TBD]
    B -.-> J[Deploy TBD]
```

## Project Structure

```
Backend/
├── App/          # FastAPI app — routes, models, engine, adapters
└── data/         # Rules (JSON) and mocked weather/market-price data
Frontend/
├── src/
│   ├── components/   # UI components
│   └── api.js        # Backend API client
Docs/             # Execution plans, user flows, architecture
```

## Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**

All commands run from the `TetraThon-Prototype/` project root.

### Backend

Run these commands from the `Backend/` directory:

1. **Create and activate a virtual environment**:
   Using Python 3.11 or 3.12 is highly recommended to ensure pre-compiled binary wheel availability.
   ```bash
   cd Backend
   python -m venv .venv

   # Activate on Windows (CMD or PowerShell):
   .venv\Scripts\activate

   # Activate on macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   If your environment lacks C++ build tools or is running a pre-release/experimental version of Python (like Python 3.14), use the fallback command to force-install pre-built binary wheels:
   ```bash
   # Standard installation:
   pip install -r requirements.txt

   # Fallback (resolves linker 'link.exe' or C++ compiler build errors):
   pip install -r requirements.txt --only-binary :all:
   ```

3. **Start the API development server**:
   ```bash
   uvicorn App.main:app --reload --port 8000
   # → Swagger Docs: http://localhost:8000/docs
   ```

### Frontend

Open a **separate terminal** — keep the backend running.

```bash
cd Frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies API calls (`/advisory`, `/locations`, etc.) to `http://localhost:8000` automatically.

### Verify

```bash
# Backend health check
curl http://localhost:8000/health
# → {"status":"OK"}

# Open http://localhost:5173 in your browser
# Click "Get Crop Advisory" → select crop + location → submit
```

## Committers

- **Om B Patel** — `byt-ctrl`
- **Dhruvin Patel** — `Dhruvinpatel06`

Built for **ArgiTech** — AgriTech Track, Navrachana University.

## License

[MIT](./LICENSE)
