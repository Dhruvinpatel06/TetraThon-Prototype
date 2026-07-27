# Remaining Issues — Post-Review Cleanup

> 5 issues remaining after Phase 1–6 review. All are low-effort fixes.

| # | Issue | File(s) | Effort |
|---|-------|---------|--------|
| 1 | ML utility functions duplicated in test files | `Backend/test_milestone_2.py`, `Backend/test_milestone_3.py` | 15 min |
| 2 | Storage dropdown missing empty placeholder | `Frontend/Src/components/UnifiedScenarioForm.jsx` | 2 min |
| 3 | Dashboard.jsx SVG icons missing `aria-label` | `Frontend/Src/components/Dashboard.jsx` | 5 min |
| 4 | Form errors not linked to inputs via `aria-describedby` | `Frontend/Src/components/AdvisoryForm.jsx`, `PostHarvestForm.jsx`, `UnifiedScenarioForm.jsx` | 20 min |
| 5 | Charts accept `realData` prop but nothing passes it | `Frontend/Src/components/Dashboard.jsx`, `SpoilageChart.jsx`, `PriceTrendChart.jsx` | 1 hr |

---

## 1. ML Utility Functions Duplicated in Test Files

**Problem:** `load_bmp_image`, `extract_features`, `relu`, `softmax` are defined in `Backend/models/ml_utils.py` (the shared module), but `Backend/test_milestone_2.py` and `Backend/test_milestone_3.py` each have their own copy.

**Fix:** Import from `ml_utils` in both test files instead of redefining.

```python
# Before (in each test file):
def relu(x): ...
def softmax(x): ...
def extract_features(path): ...

# After:
from models.ml_utils import relu, softmax, extract_features, load_bmp_image
```

---

## 2. Storage Dropdown Missing Empty Placeholder

**Problem:** `UnifiedScenarioForm.jsx` storage `<select>` has no empty `<option value="">` — browser shows "Open Yard" as visual default even though state is `''`.

**Fix:** Add placeholder option consistent with other dropdowns.

```jsx
<!-- Before -->
<select id="storage-condition" ...>
  <option value="open">Open Yard</option>

<!-- After -->
<select id="storage-condition" ...>
  <option value="">-- Select storage type --</option>
  <option value="open">Open Yard</option>
```

---

## 3. Dashboard.jsx SVG Icons Missing `aria-label`

**Problem:** `AdvisoryResult.jsx` has `aria-label` on advisory icons, but `Dashboard.jsx` does not. Screen readers skip the icons.

**Fix:** Add `aria-label` to the 3 advisory SVGs in `Dashboard.jsx`.

```jsx
<!-- Before -->
<svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">

<!-- After -->
<svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-label="Irrigation advisory icon">
```

Apply to irrigation, fertiliser, and pest icons.

---

## 4. Form Errors Not Linked to Inputs

**Problem:** Error divs have `role="alert"` but inputs don't reference them via `aria-describedby`. Screen readers don't announce errors in context.

**Fix:** Add `aria-describedby` to each input pointing to the error div's ID.

```jsx
<!-- Before -->
<div id="advisory-error" role="alert">{error}</div>
<select id="location" ...>

<!-- After -->
<div id="advisory-error" role="alert">{error}</div>
<select id="location" aria-describedby={error ? "advisory-error" : undefined} ...>
```

Apply to all form `<select>` and `<input>` elements that have validation errors.

---

## 5. Charts Use Synthetic Data — `realData` Prop Never Passed

**Problem:** `SpoilageChart` and `PriceTrendChart` accept a `realData` prop and fall back to random data when it's `null`. But `Dashboard.jsx` never passes `realData`, so charts always show synthetic data.

**Fix (Option A — wire backend data):**
1. Add a backend endpoint that returns price history for a crop/location.
2. Fetch in `Dashboard.jsx` and pass as `realData` to both charts.

**Fix (Option B — remove the prop):**
If real data isn't available yet, remove the dead `realData` prop and document that charts are illustrative.

---

## Execution Order

```
1. ML utils dedup       (quick, no risk)
2. Storage placeholder   (1 line)
3. Dashboard aria-labels (3 lines)
4. aria-describedby      (all forms)
5. Chart data wiring     (biggest change, do last)
```

All 5 can be committed together or one-by-one. Estimated total: **~1.5 hours**.
