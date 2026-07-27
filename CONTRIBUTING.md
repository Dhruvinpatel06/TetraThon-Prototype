# Contributing to AgriTech

Thank you for your interest in contributing to AgriTech. This document provides guidelines and instructions for contributing to this project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on what is best for the project and the team
- Give and receive feedback gracefully

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Git | Latest | Version control |

### Installation

**Backend:**

```bash
cd Backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
set AUTO_SEED=true
uvicorn App.main:app --reload --port 8000
```

**Frontend:**

```bash
cd Frontend
npm install
npm run dev
```

The frontend starts at `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

---

## Project Architecture

```
TetraThon-Prototype/
├── Backend/
│   ├── App/
│   │   ├── main.py              # Application entry point, middleware, CORS
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── database.py          # SQLite connection and session management
│   │   ├── seed.py              # Database seeding logic
│   │   ├── routers/             # API endpoint definitions
│   │   │   ├── advisory.py      # POST /api/advisory
│   │   │   ├── post_harvest.py  # POST /api/post-harvest
│   │   │   ├── locations.py     # GET /api/locations
│   │   │   ├── crops.py         # GET /api/crops
│   │   │   ├── health.py        # GET /api/health
│   │   │   └── rules.py         # GET /api/rules
│   │   ├── engine/              # Decision engines
│   │   │   ├── advisory.py      # Crop advisory generation
│   │   │   ├── decision.py      # Post-harvest recommendation logic
│   │   │   ├── spoilage.py      # Produce decay calculations
│   │   │   └── transport.py     # Haversine distance and transport cost
│   │   └── adapters/            # External API integrations
│   │       ├── weather.py       # OpenWeatherMap adapter
│   │       ├── market_prices.py # Agmarknet price data adapter
│   │       └── config.py        # API keys and configuration
│   ├── data/                    # Static data files
│   │   ├── irrigation_rules.json
│   │   ├── fertiliser_rules.json
│   │   ├── pest_rules.json
│   │   └── mandi_prices.csv
│   └── requirements.txt
├── Frontend/
│   ├── Src/
│   │   ├── App.jsx              # Root component with view routing
│   │   ├── api.js               # API wrapper with timeout and retry
│   │   └── components/          # Reusable UI components
│   │       ├── Layout.jsx
│   │       ├── AdvisoryForm.jsx
│   │       ├── AdvisoryResult.jsx
│   │       ├── PostHarvestForm.jsx
│   │       ├── PostHarvestResult.jsx
│   │       ├── UnifiedScenarioForm.jsx
│   │       ├── Dashboard.jsx
│   │       ├── SpoilageChart.jsx
│   │       ├── PriceTrendChart.jsx
│   │       ├── HealthCheck.jsx
│   │       ├── LocationList.jsx
│   │       └── CropList.jsx
│   └── package.json
└── Docs/                        # Project documentation
    ├── diagrams/                # Architecture and flow diagrams
    ├── plans/                   # Execution plans
    ├── reports/                 # Completion reports and lessons learned
    ├── guides/                  # Contributing and demo guides
    ├── reference/               # Tech stack, API docs, decision logic
    └── screenshots/             # Application screenshots
```

---

## Development Workflow

### Branch Naming

Use descriptive branch names with a type prefix:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New feature | `feat/leaf-classification-api` |
| `fix/` | Bug fix | `fix/spoilage-negative-values` |
| `docs/` | Documentation | `docs/api-error-responses` |
| `refactor/` | Code restructuring | `refactor/engine-modularization` |

### Commit Messages

Write clear, concise commit messages:

```
Add weather risk multiplier to pest advisory

- Factor in humidity and temperature conditions
- Escalate risk level when conditions match raises_risk_if rules
- Update confidence scoring for weather-dependent advisories
```

### Development Process

1. Create a branch from `main`
2. Make changes in small, focused commits
3. Write or update tests
4. Run the full test suite
5. Submit a pull request

---

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Use docstrings for public functions
- Keep functions under 50 lines
- Handle exceptions explicitly — no bare `except` clauses

```python
def generate_advisories(
    location_name: str,
    crop_name: str,
    sowing_date_str: str,
    weather_observation: str | None
) -> list[dict]:
    """Generate ranked advisories for a farmer session."""
    ...
```

### JSX (Frontend)

- Use functional components exclusively
- Use hooks for state and side effects
- One component per file
- File name matches component name
- Use Tailwind CSS for all styling

```jsx
export default function AdvisoryForm({ locations, crops, onSubmitSuccess, onCancel }) {
  const [formData, setFormData] = useState({ ... });
  // ...
}
```

### General

- No hardcoded values — use constants or configuration
- No `console.log` or `print` debugging in committed code
- Comment only non-obvious logic — code should be self-documenting

---

## Testing Requirements

### Backend

```bash
cd Backend
pytest
```

- Write tests for all engine functions
- Test edge cases (zero quantity, future dates, missing data)
- Aim for >80% coverage on engine modules

### Frontend

```bash
cd Frontend
npm test
```

- Test component rendering
- Test user interactions
- Test API error handling

---

## Pull Request Process

### Before Submitting

- [ ] Code runs without errors
- [ ] All tests pass
- [ ] No debugging artifacts (`console.log`, `print`, commented-out code)
- [ ] API documentation updated (if endpoint changed)
- [ ] Components are reusable (not hardcoded to specific values)

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Screenshots (if applicable)
```

### Review Criteria

1. **Functionality:** Does it work as intended?
2. **Code quality:** Is it clean, readable, and maintainable?
3. **Testing:** Are there adequate tests?
4. **Documentation:** Are docs updated?

---

## Adding New Features

### Adding a New Crop

1. Add crop definition to `Backend/data/crops.json`
2. Add irrigation rules to `Backend/data/irrigation_rules.json`
3. Add fertiliser rules to `Backend/data/fertiliser_rules.json`
4. Add pest rules to `Backend/data/pest_rules.json`
5. Add historical price data to `Backend/data/mandi_prices.csv`
6. Set `AUTO_SEED=true` and restart the backend

### Adding a New API Endpoint

1. Create a new router file in `Backend/App/routers/`
2. Define request/response schemas in `Backend/App/schemas.py`
3. Register the router in `Backend/App/main.py`:
   ```python
   app.include_router(new_router.router, prefix="/api")
   ```
4. Write tests in `Backend/tests/`
5. Update `Docs/reference/api-documentation.md`

### Adding a New Frontend Component

1. Create the component file in `Frontend/Src/components/`
2. Import and render it in `App.jsx`
3. Follow existing patterns for props, state, and styling

---

## Questions?

If you have questions about contributing, reach out to the team before submitting a PR.

---

*— AgriTech Project —*
