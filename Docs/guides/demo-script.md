# Demo Script

Step-by-step click-through for a 5-minute presentation.

---

## Pre-Demo Checklist

- [ ] Backend running at `https://agritech-backend.onrender.com/api/health`
- [ ] Frontend running at `https://agritech-frontend.vercel.app`
- [ ] Browser zoom set to 100%
- [ ] Browser window maximized
- [ ] Close all unnecessary tabs
- [ ] Clear browser console (F12 → Console → Clear)

---

## Step 1: Home Screen (30 seconds)

**Action:** Open the app URL.

**What judges see:** Home screen with 3 cards — Unified Dashboard, Crop Advisory, Post-Harvest Planner.

**Say:** "AgriTech is a dual-engine agricultural decision support system. It combines crop growth advisories with post-harvest loss minimization. Let me show you both modules."

**Click:** None. Just describe the three options.

---

## Step 2: Crop Advisory (90 seconds)

**Action:** Click "Crop Advisory" card.

**What judges see:** Form with dropdowns for location, crop, sowing date, and weather observation.

**Fill in:**
| Field | Value |
|-------|-------|
| Location | Ahmedabad |
| Crop | Cotton |
| Sowing Date | 2026-06-15 (approximately 40 days ago) |
| Weather Observation | Hot and Dry |

**Click:** "Get Advisory"

**What judges see:** 3 advisory cards — Irrigation, Fertiliser, Pest — each with confidence tag and plain-language explanation.

**Say:** "The system calculates the growth stage from the sowing date, applies weather risk multipliers, and returns the top 3 prioritized advisories. Notice the confidence tags — High when we have weather data, Medium when we don't."

**Point out:**
- Irrigation advisory shows water depth and frequency
- Fertiliser advisory shows NPK dosage
- Pest advisory shows risk level and weather impact

---

## Step 3: Post-Harvest Planner (90 seconds)

**Action:** Click "Home" → Click "Post-Harvest Plan" card.

**What judges see:** Form with dropdowns for crop, quantity, storage, and location.

**Fill in:**
| Field | Value |
|-------|-------|
| Crop | Cotton |
| Quantity | 50 quintals |
| Storage | Warehouse |
| Location | Ahmedabad |

**Click:** "Generate Plan"

**What judges see:** Recommendation card with:
- Recommended action (Transport to Best Market)
- Expected return in rupees
- Comparison of 3 options (Sell Now, Store, Transport)
- Reason text explaining why

**Say:** "The system compares selling now at the nearest market, storing for 14 days, and transporting to a more profitable market. It factors in spoilage rates, storage costs, and transport expenses. In this case, transporting to Surat yields ₹12,500 more than selling locally."

**Point out:**
- The "Sell Now" option shows nearest market and transport cost
- The "Store" option shows spoilage loss and storage cost
- The "Transport" option shows the best market and distance

---

## Step 4: Unified Dashboard (60 seconds)

**Action:** Click "Home" → Click "Open Unified Dashboard" button.

**What judges see:** Single form combining both modules.

**Fill in:** Same values as before (Ahmedabad, Cotton, 2026-06-15, Hot and Dry, 50 quintals, Warehouse).

**Click:** "Run Full Analysis"

**What judges see:** Side-by-side dashboard with:
- Left column: 3 advisory cards from Module A
- Right column: Post-harvest recommendation from Module B
- Bottom: Interactive charts (price trends, spoilage curves)

**Say:** "The unified dashboard triggers both modules concurrently using Promise.all. The farmer gets a complete picture — what to do now (advisory) and what to do after harvest (post-harvest plan) — in one view."

**Point out:**
- The charts show 90-day price trends across 5 markets
- The spoilage curves show value loss over 30 days for each storage type

---

## Step 5: Close (30 seconds)

**Action:** Click "Home" to return to home screen.

**Say:** "AgriTech combines real-time weather data, historical market prices, and agronomic rules to give farmers actionable, data-driven decisions. The system is designed to scale — adding new crops, locations, and markets is a configuration change, not a code change. Thank you."

---

## Timing Summary

| Step | Duration | Cumulative |
|------|----------|------------|
| Home Screen | 30s | 0:30 |
| Crop Advisory | 90s | 2:00 |
| Post-Harvest | 90s | 3:30 |
| Dashboard | 60s | 4:30 |
| Close | 30s | 5:00 |

---

## Backup Plan

If live API fails during demo:
1. The mock fallback activates automatically
2. Say: "The system gracefully degrades to cached data when external APIs are unavailable"
3. Continue the demo — judges will see the same results

If the app is slow:
1. Say: "The backend is hosted on Render's free tier — it may take a moment to wake up"
2. Use the loading time to explain the architecture

---

*— Phase 0 Submission —*
