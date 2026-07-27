# User Flows

## Primary User Journey

```mermaid
flowchart TD
    Start["Farmer opens AgriTech App"] --> Home["Home Screen — Choose Module"]

    Home -->|Module A| AdvisoryFlow
    Home -->|Module B| PostHarvestFlow
    Home -->|Both| UnifiedFlow

    subgraph AdvisoryFlow ["Module A — Crop Advisory"]
        A1["Select location, crop, sowing date"] --> A2["Optional — Upload leaf photo"]
        A2 --> A3["Submit → POST /api/advisory"]
        A3 --> A4["Backend calculates growth stage"]
        A4 --> A5["Rule engine matches advisories"]
        A5 --> A6["Weather risk multipliers applied"]
        A6 --> A7["Top 3 advisories ranked by confidence"]
    end

    subgraph PostHarvestFlow ["Module B — Post-Harvest Planner"]
        B1["Select crop, quantity, storage, location"] --> B2["Submit → POST /api/post-harvest"]
        B2 --> B3["Spoilage model estimates daily value loss"]
        B3 --> B4["Transport model costs to 5 markets"]
        B4 --> B5["Decision engine compares options"]
        B5 --> B6["Recommends: Sell Now / Store / Transport"]
    end

    subgraph UnifiedFlow ["Unified Dashboard — Both Modules"]
        U1["Single form — all inputs"] --> U2["Promise.all — concurrent API calls"]
        U2 --> U3["Advisory + Post-Harvest results"]
        U3 --> U4["Side-by-side dashboard view"]
        U4 --> U5["Interactive charts — price trends, spoilage curves"]
    end

    A7 --> ResultsA["Display 3 advisory cards with confidence tags"]
    B6 --> ResultsB["Display recommendation + expected return"]
    U5 --> ResultsU["Full dashboard with charts and metrics"]

    ResultsA --> Next["Farmer takes action"]
    ResultsB --> Next
    ResultsU --> Next

    style Start fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style Home fill:#f0f9ff,stroke:#0284c7
    style AdvisoryFlow fill:#ecfdf5,stroke:#059669
    style PostHarvestFlow fill:#f0f9ff,stroke:#0284c7
    style UnifiedFlow fill:#fefce8,stroke:#ca8a04
    style Next fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
```

---

## Flow Descriptions

### Module A — Crop Advisory
Farmer selects location, crop, and sowing date. The system calculates the current growth stage, applies weather risk multipliers, and returns the top 3 prioritized advisories (irrigation, fertiliser, pest control) with confidence scores.

### Module B — Post-Harvest Planner
Farmer selects crop, quantity, storage condition, and location. The system estimates daily spoilage costs, calculates transport expenses to nearby markets, and recommends the option with the highest net return.

### Unified Dashboard
Single form triggers both modules concurrently. Results display side-by-side with interactive charts showing 90-day price trends and 30-day spoilage curves.

---

*— Phase 0 Submission —*
