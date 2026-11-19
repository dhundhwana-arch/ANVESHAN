# ANVESHAN — Final Reality & Integrity Audit

**Project:** ANVESHAN — Advanced Scientific Research & Discovery Platform
**Founder & Developer:** Divyesh Bambhaniya
**Audit Date:** 2026-11-19

This audit strictly classifies every component using the required honesty categories (A–G). No feature is labeled working merely because its UI exists.

## Feature-by-Feature Classification

### 1. Mathematical Symbolic & Statistical Engine — **A. REAL AND WORKING**
- **Files:** `backend/engines/math_engine.py`, `backend/main.py` (`/api/math/symbolic`, `/api/math/statistics`, `/api/math/monte-carlo-pi`)
- **Implementation:** Real SymPy symbolic algebra/calculus with restricted parser sandbox, NumPy/SciPy descriptive statistics, Shapiro-Wilk test, one-sample t-test, OLS linear regression (with explicit correlation-vs-causation warning), and deterministic seeded Monte Carlo estimation.
- **Test Evidence:** 4/4 tests in `tests/test_math_engine.py` + E2E test in `tests/test_api_e2e.py` passed.
- **Limitations:** Expression length capped at 300 chars; only whitelisted univariate/multivariate standard math symbols supported.

### 2. Physics Simulation Engine — **A. REAL AND WORKING**
- **Files:** `backend/engines/physics_engine.py`, `backend/main.py` (`/api/physics/oscillator`, `/api/physics/projectile`, `/api/physics/decay`)
- **Implementation:** Real SciPy `solve_ivp` (RK45, `rtol=1e-8`, `atol=1e-10`) ODE solvers compared directly against exact closed-form analytical solutions with RMSE, max absolute error, and energy/non-negativity checks.
- **Test Evidence:** 4/4 tests in `tests/test_physics_engine.py` + E2E test passed (`max_abs_error < 1e-5` m for all 3 oscillator regimes; vacuum projectile error `< 1e-4` m).
- **Limitations:** Covers 3 deterministic classical/nuclear models in v1.0; PDEs and quantum systems are not yet implemented.

### 3. Immutable Experiment Ledger & Reproducibility Reruns — **A. REAL AND WORKING**
- **Files:** `backend/database.py`, `backend/engines/hypothesis_engine.py` (`rerun_experiment`)
- **Implementation:** Real SQLite database with `BEFORE UPDATE` and `BEFORE DELETE` triggers raising `ABORT`, SHA-256 input/parameter checksums, live Python/SciPy/SymPy version capture, and child-linked deterministic reruns (`max_numeric_diff == 0.0`).
- **Test Evidence:** `tests/test_database.py`, `tests/test_hypothesis_engine.py`, and `tests/test_api_e2e.py` passed.

### 4. Hypothesis Falsification Engine — **A. REAL AND WORKING**
- **Files:** `backend/engines/hypothesis_engine.py`, `backend/main.py` (`/api/hypotheses/*`)
- **Implementation:** Stores assumptions, falsifiable predictions, test configs, and acceptance criteria; runs actual engines; preserves failed/falsified runs honestly (`FALSIFIED_BY_COMPUTATION` / `FAILED_EXPERIMENT`); explicitly notes computational support is not universal proof.
- **Test Evidence:** `test_hypothesis_supported_and_falsified_paths` passed for both supported and deliberately falsified hypotheses.

### 5. Responsive Research Laboratory UI — **B. REAL BUT NOT FULLY VERIFIED (Headless Browser Not Run)**
- **Files:** `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`
- **Implementation:** Real HTML/CSS/JS calling real FastAPI endpoints via `fetch()`, rendering live Canvas plots from actual backend trajectories/curves, live SQLite telemetry counts, and required footer (`Developer by Divyesh Bambhaniya`).
- **Test Evidence:** Serving, brand footer, security headers, and every backing API endpoint verified via `TestClient`; interactive browser click/layout verification on an Android tablet requires running locally in a browser.

### 6. Scientific Literature APIs (OpenAlex, arXiv, PubChem) — **D. NOT CONNECTED (in Offline Build Sandbox)**
- **Files:** `backend/engines/literature_engine.py`
- **Implementation:** Real `httpx` clients targeting official endpoints (`https://api.openalex.org/works`, `https://export.arxiv.org/api/query`, `https://pubchem.ncbi.nlm.nih.gov/rest/pug/...`) with rate-limit guards (3s arXiv, 200ms PubChem) and honest `NOT_CONNECTED` error handling.
- **Test Evidence:** Schema parsers verified with explicitly labeled test fixtures (`tests/test_literature_engine.py`); offline handling verified. Live network calls require running outside the offline sandbox.

### 7. Gemini AI Synthesis Adapter — **D. NOT CONNECTED (API Key Not Configured)**
- **Files:** `backend/engines/ai_provider.py`
- **Implementation:** Replaceable `AIProvider` interface + `GeminiProvider` targeting `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` via `GEMINI_API_KEY`.
- **Test Evidence:** `tests/test_ai_provider.py` verified honest `NOT_CONFIGURED` status with `response: null` (zero fake AI output).

### 8. Literature Parser Test Fixtures — **E. DEMO OR MOCK ONLY (Isolated Test Fixtures)**
- **Files:** `tests/test_literature_engine.py`
- **Details:** Sample OpenAlex JSON, arXiv Atom XML, and PubChem JSON payloads exist strictly inside unit tests to verify parsing logic offline; never used in production endpoints.

### 9. Scripted Fake Features — **NONE (0)**
- Zero hardcoded scientific results, zero fake AI chat, zero scripted agent activity, zero fabricated citations.

### 10. Multi-User Auth, CSV Dataset Upload, Direct GitHub Push & Cloud Deployment — **G. NOT IMPLEMENTED / BLOCKED**
- Multi-user JWT/OAuth and CSV upload workbench are planned for v1.2.
- Direct `git push` to GitHub and Render deployment are blocked by offline sandbox / account authorization and delivered via `ANVESHAN_v1_repo.zip` + `push_to_github.sh`.
