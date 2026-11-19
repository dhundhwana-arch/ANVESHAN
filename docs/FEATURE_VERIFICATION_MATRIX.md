# ANVESHAN — Feature Verification Matrix

| Feature | Implementation File(s) | Status | Verification Evidence |
| --- | --- | --- | --- |
| Immutable SQLite Experiment Ledger | `backend/database.py` | **REAL AND WORKING** | `tests/test_database.py` (`test_experiment_immutability_triggers`) passed |
| SymPy Symbolic Engine + Injection Guard | `backend/engines/math_engine.py` | **REAL AND WORKING** | `tests/test_math_engine.py` (calculus + 4 injection payloads blocked) passed |
| NumPy/SciPy Statistics & Regression | `backend/engines/math_engine.py` | **REAL AND WORKING** | `tests/test_math_engine.py` (`test_statistics_and_regression_accuracy`) passed |
| Seeded Monte Carlo Pi Estimation | `backend/engines/math_engine.py` | **REAL AND WORKING** | `tests/test_math_engine.py` (`test_monte_carlo_deterministic_seed`) passed |
| Physics: Damped Harmonic Oscillator | `backend/engines/physics_engine.py` | **REAL AND WORKING** | `tests/test_physics_engine.py` (all 3 regimes < 1e-5 m error, energy non-increasing) passed |
| Physics: 2D Projectile with Air Drag | `backend/engines/physics_engine.py` | **REAL AND WORKING** | `tests/test_physics_engine.py` (vacuum limit < 1e-4 m error + drag reduction) passed |
| Physics: Radioactive Decay | `backend/engines/physics_engine.py` | **REAL AND WORKING** | `tests/test_physics_engine.py` (half-life exact match) passed |
| Hypothesis Falsification & Reruns | `backend/engines/hypothesis_engine.py` | **REAL AND WORKING** | `tests/test_hypothesis_engine.py` (pass, falsified, and `max_numeric_diff == 0.0` rerun) passed |
| OpenAlex / arXiv / PubChem Clients | `backend/engines/literature_engine.py` | **NOT CONNECTED (in offline sandbox)** | Schema parsers verified via fixtures; live outbound HTTP blocked by offline build sandbox |
| Gemini API Synthesis Adapter | `backend/engines/ai_provider.py` | **NOT CONNECTED (key not set)** | `tests/test_ai_provider.py` verified honest `NOT_CONFIGURED` behavior with zero fake output |
| Responsive Research Lab UI | `frontend/index.html`, `styles.css`, `app.js` | **REAL AND WORKING** | `tests/test_api_e2e.py` verified serving, brand footer, security headers, and live API endpoints |
