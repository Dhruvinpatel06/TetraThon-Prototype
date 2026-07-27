# Lessons Learned

## What Worked Well

### 1. Sequential Chunk Execution
Building one chunk at a time (P1 → P2 → P3 → P4) eliminated merge conflicts. The app was always in a working state. Each person could pick up where the last left off.

### 2. SQLite Over PostgreSQL
Zero setup meant we could demo on any machine. No database server to configure, no connection strings to manage. A single `agritech.db` file was portable and crash-safe.

### 3. Mock Fallbacks for External APIs
Both OpenWeatherMap and Agmarknet APIs had mock data fallbacks. During the demo, if the API was slow or the key expired, the app still worked seamlessly. Judges never saw an error.

### 4. Pydantic Validation at the Boundary
Catching bad input at the API layer (before it hit the engine) saved hours of debugging. Every endpoint returned meaningful error messages.

### 5. State-Based View Routing
Instead of React Router, we used a simple `view` state variable. This eliminated routing configuration, URL management, and deep linking complexity — all unnecessary for a single-page hackathon demo.

---

## What We'd Do Differently

### 1. Start with API Contracts First
We built the backend, then the frontend. If we'd defined the API contracts (request/response schemas) first, both teams could have worked in parallel from day one.

### 2. Seed Data Earlier
Database seeding was an afterthought. We should have created the seed script in Chunk 1, not Chunk 3. It would have made frontend development faster with real data.

### 3. Add Error Boundaries Sooner
Frontend error handling was added late. A single API failure could crash the entire app. Error boundaries should be in place from the start.

### 4. Write Tests During Development
We wrote tests at the end. If we'd written them alongside the code, we would have caught the transport cost calculation bug earlier (it was returning negative values for zero quantity).

### 5. Separate Config from Code
API keys and configuration were initially hardcoded. Environment variables should be set up from day one, not as a last-minute security fix.

---

## Technical Debt to Address

| Item | Priority | Effort |
|------|----------|--------|
| Add input validation for sowing date (prevent future dates) | High | 1 hour |
| Add retry logic for external API calls | Medium | 2 hours |
| Add loading states for all API calls | Medium | 1 hour |
| Add unit tests for engine functions | High | 4 hours |
| Add TypeScript to frontend | Low | 8 hours |
| Add error logging to backend | Medium | 2 hours |

---

## Advice for Future Teams

1. **Demo-proof your app.** Assume the internet will fail. Have mock data ready.
2. **Build the boring stuff first.** Database, API contracts, error handling — before the fancy UI.
3. **One person builds at a time.** Parallel work sounds efficient but creates merge conflicts and broken states.
4. **Keep the pitch deck updated.** Don't scramble at the end to document what you built.
5. **Test on a different machine.** If it only works on your laptop, it doesn't work.

---

*— Phase 0 Submission —*
