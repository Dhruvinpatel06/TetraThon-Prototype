# Decision-Making Processes & Impact Metrics

## How the System Makes Decisions

### Module A - Crop Advisory Engine

```
Input: Location + Crop + Sowing Date + Weather Observation
        ↓
Calculate days since sowing → Determine growth stage
        ↓
Load rules from JSON files (irrigation, fertiliser, pest)
        ↓
Fetch weather forecast (live API → fallback to mock)
        ↓
Apply weather risk multipliers to pest advisories
        ↓
Generate 3 ranked advisories with confidence scores
        ↓
Output: Top 3 advisories (irrigation, fertiliser, pest)
```

**Decision Logic:**
1. **Growth Stage Calculation:** `days_since_sowing = today - sowing_date`. Matched against `days_range` in rule files.
2. **Weather Risk Multiplier:** If weather conditions match `raises_risk_if` in pest rules, risk level escalates (Low → Medium → High).
3. **Confidence Scoring:**
   - `High` = Weather observation provided + exact stage match
   - `Medium` = Fallback stage or no weather observation
   - `Low` = API failure or invalid input

### Module B - Post-Harvest Decision Engine

```
Input: Crop + Quantity + Storage + Location
        ↓
Find nearest market (Haversine distance)
        ↓
Calculate 3 options:
  Option 1: Sell Now → (price × quantity) - transport cost
  Option 2: Store 14 days → future price - spoilage - storage cost
  Option 3: Transport to best market → best market price - transport cost
        ↓
Compare net returns → Pick highest
        ↓
Output: Recommendation + expected return + reason
```

**Decision Logic:**
1. **Sell Now:** Nearest market price × quantity - transport cost (₹5/km/quintal, ₹500 minimum).
2. **Store:** Future price (14 days ahead) - spoilage loss (storage-type dependent) - storage cost (₹2/quintal/day warehouse, ₹5/quintal/day cold storage).
3. **Transport:** Best market price × quantity - transport cost to that market.
4. **Hold/Consult:** If all 3 options yield negative net returns.

---

## Impact Metrics

### Quantified Benefits

| Metric | Before (Manual) | After (AgriTech) | Improvement |
|--------|-----------------|------------------|-------------|
| **Advisory generation time** | 2-3 days (visit extension office) | Instant (< 2 seconds) | 99.9% faster |
| **Decision accuracy** | Gut feeling / neighbor advice | Data-driven (1,800 price records + weather) | Measurable |
| **Post-harvest loss** | 15-25% of produce value | Reduced via optimal timing | Est. 10-15% savings |
| **Transport cost** | Fixed (always nearest market) | Dynamic (compares 5 markets) | Est. 5-12% savings |
| **Weather awareness** | Manual radio/TV forecasts | Real-time 7-day API integration | Proactive vs reactive |

### Real-World Example

**Scenario:** Farmer with 50 quintals of Cotton in Ahmedabad

| Option | Revenue | Costs | Net Return |
|--------|---------|-------|------------|
| Sell Now (Ahmedabad) | ₹3,10,000 | ₹1,250 transport | ₹3,08,750 |
| Store 14 days (warehouse) | ₹3,20,000 | ₹1,400 storage + ₹4,960 spoilage | ₹3,13,640 |
| Transport to Surat | ₹3,25,000 | ₹3,750 transport | ₹3,21,250 |

**System Recommendation:** Transport to Surat → **₹12,500 more** than selling locally.

### Coverage

| Item | Count |
|------|-------|
| Supported crops | 4 (Cotton, Wheat, Groundnut, Tomato) |
| Supported locations | 5 (Ahmedabad, Vadodara, Surat, Rajkot, Anand) |
| APMC markets compared | 5 |
| Price data points | 1,800+ |
| Advisory types | 3 (irrigation, fertiliser, pest) |
| Decision options | 4 (sell, store, transport, hold) |

---

*- Phase 0 Submission -*
