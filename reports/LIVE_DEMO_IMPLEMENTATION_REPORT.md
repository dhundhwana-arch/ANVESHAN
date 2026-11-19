# ANVESHAN v1.2 — Interactive Live Demo Implementation Report

**Project:** ANVESHAN — Advanced Scientific Research & Discovery Platform
**Founder & Developer:** Divyesh Bambhaniya
**Git Branch:** `feat/anveshan-v1-core`
**Commit SHA:** `74b6fbccd43d416087c584548b77d9d6ed560ae6` (`74b6fbc`)
**Date:** 2026-11-19

## 1. Interactive Live Demos Implemented & Backend Endpoints Connected

| # | Live Demo Card / Lab | Connected Real Backend Endpoint(s) | Visualization / Output |
| --- | --- | --- | --- |
| 1 | Mathematical Engine (Symbolic, Statistics/OLS, Monte Carlo &pi;) | `POST /api/math/symbolic`, `POST /api/math/statistics`, `POST /api/math/monte-carlo-pi` | Real SymPy/SciPy output + live Canvas function & regression plots |
| 2 | Physics Simulation Engine (All 5 ODE Models) | `POST /api/physics/oscillator`, `/projectile`, `/decay`, `/cooling`, `/logistic` | Real SciPy RK45 vs exact analytical Canvas plots + error metrics |
| 3 | Hypothesis Verification Chamber | `POST /api/hypotheses`, `POST /api/hypotheses/{id}/verify` | Real `SUPPORTED_BY_COMPUTATION` / `FALSIFIED_BY_COMPUTATION` evaluation |
| 4 | CSV Data Analysis Workbench | `POST /api/datasets/analyze` | Real CSV upload (or clearly labeled Sample Dataset) + SHA-256 + Canvas scatter/fit plot |
| 5 | Experiment Ledger & Reproducibility | `GET /api/experiments`, `POST /api/experiments/{id}/rerun` | Real Experiment ID, SHA-256 checksum, deterministic rerun diff |
| 6 | Scientific Literature Explorer | `POST /api/literature/search` | Real OpenAlex/arXiv/PubChem clients; honest `NOT_CONNECTED` when offline |
| 7 | Evidence Export (Markdown & BibTeX) | `GET /api/experiments/{id}/report`, `GET /api/literature/export/bibtex` | Real `.md` and `.bib` file downloads from SQLite records |
| 8 | AI Synthesis Adapter | `POST /api/ai/analyze` | Real Gemini API when `GEMINI_API_KEY` set; honest `NOT_CONFIGURED` otherwise |

## 2. Automated Test Evidence
- **Command:** `python3 -m unittest discover -s tests -v`
- **Result:** **26 passed, 0 failed, 0 skipped** (includes 2 new UI/endpoint wiring tests in `tests/test_live_demo_ui.py`)

```text
test_missing_api_key_reports_not_configured (test_ai_provider.TestAIProviderHonesty.test_missing_api_key_reports_not_configured) ... ok
test_frontend_served_with_brand_footer_and_security_headers (test_api_e2e.TestAPIEndToEnd.test_frontend_served_with_brand_footer_and_security_headers) ... ok
test_full_vertical_research_workflow (test_api_e2e.TestAPIEndToEnd.test_full_vertical_research_workflow) ... ok
test_v1_2_dataset_cooling_and_export_endpoints (test_api_e2e.TestAPIEndToEnd.test_v1_2_dataset_cooling_and_export_endpoints) ... ok
test_experiment_immutability_triggers (test_database.TestDatabaseIntegrity.test_experiment_immutability_triggers) ... ok
test_literature_upsert_and_counts (test_database.TestDatabaseIntegrity.test_literature_upsert_and_counts) ... ok
test_csv_stats_correlation_and_regression (test_dataset_engine.TestDatasetEngine.test_csv_stats_correlation_and_regression) ... ok
test_empty_and_invalid_csv_rejected (test_dataset_engine.TestDatasetEngine.test_empty_and_invalid_csv_rejected) ... ok
test_bibtex_and_markdown_report_generation (test_export_engine.TestExportAndExtendedPhysics.test_bibtex_and_markdown_report_generation) ... ok
test_thermal_cooling_and_logistic_growth_accuracy (test_export_engine.TestExportAndExtendedPhysics.test_thermal_cooling_and_logistic_growth_accuracy) ... ok
test_deterministic_rerun_reproducibility (test_hypothesis_engine.TestHypothesisAndReproducibility.test_deterministic_rerun_reproducibility) ... ok
test_hypothesis_supported_and_falsified_paths (test_hypothesis_engine.TestHypothesisAndReproducibility.test_hypothesis_supported_and_falsified_paths) ... ok
test_arxiv_atom_parser_fixture (test_literature_engine.TestLiteratureParsersAndOfflineHandling.test_arxiv_atom_parser_fixture) ... ok
test_offline_returns_honest_not_connected (test_literature_engine.TestLiteratureParsersAndOfflineHandling.test_offline_returns_honest_not_connected) ... ok
test_openalex_parser_fixture (test_literature_engine.TestLiteratureParsersAndOfflineHandling.test_openalex_parser_fixture) ... ok
test_pubchem_parser_fixture (test_literature_engine.TestLiteratureParsersAndOfflineHandling.test_pubchem_parser_fixture) ... ok
test_frontend_js_wires_all_real_backend_endpoints (test_live_demo_ui.TestLiveDemoWebsite.test_frontend_js_wires_all_real_backend_endpoints) ... ok
test_live_demo_navigation_cards_and_brand_identity (test_live_demo_ui.TestLiveDemoWebsite.test_live_demo_navigation_cards_and_brand_identity) ... ok
test_monte_carlo_deterministic_seed (test_math_engine.TestMathEngine.test_monte_carlo_deterministic_seed) ... ok
test_statistics_and_regression_accuracy (test_math_engine.TestMathEngine.test_statistics_and_regression_accuracy) ... ok
test_symbolic_differentiate_and_integrate (test_math_engine.TestMathEngine.test_symbolic_differentiate_and_integrate) ... ok
test_symbolic_security_injection_blocked (test_math_engine.TestMathEngine.test_symbolic_security_injection_blocked) ... ok
test_invalid_physics_parameters_rejected (test_physics_engine.TestPhysicsEngine.test_invalid_physics_parameters_rejected) ... ok
test_oscillator_all_three_damping_regimes (test_physics_engine.TestPhysicsEngine.test_oscillator_all_three_damping_regimes) ... ok
test_projectile_vacuum_matches_analytical_and_drag_reduces_range (test_physics_engine.TestPhysicsEngine.test_projectile_vacuum_matches_analytical_and_drag_reduces_range) ... ok
test_radioactive_decay_half_life_accuracy (test_physics_engine.TestPhysicsEngine.test_radioactive_decay_half_life_accuracy) ... ok

----------------------------------------------------------------------
Ran 26 tests in 0.389s

OK
```

## 3. Features Not Connected / Requiring External Keys or Network
- **OpenAlex, arXiv, PubChem live queries:** Implemented and parser-tested, but require an internet-connected host (returns honest `NOT_CONNECTED` in offline sandbox).
- **Gemini AI Synthesis:** Requires `GEMINI_API_KEY` configured in server `.env` (returns honest `NOT_CONFIGURED` when unset; all core engines remain 100% functional without it).

## 4. Browser & Mobile Verification Status
- **Verified via FastAPI `TestClient`:** HTML delivery, all 9 navigation sections, "Explore Live Demos" cards, brand identity footer (`Developer by Divyesh Bambhaniya`), static CSS/JS serving, security headers, and every backend API route.
- **Not Yet Executed:** Live interactive click-testing in a real Android tablet/mobile browser (must be verified once opened locally in Termux or deployed on Render).

## 5. Deployment Status & Public Website URL
- **Free Deployment Feasibility:** **YES** — existing `render.yaml` is already configured for Render's free web service tier (`plan: free`, `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`), with zero paid resources or custom domain required.
- **Current Deployment Status:** **NOT DEPLOYED (BLOCKED BY EXTERNAL ACCOUNT AUTHORIZATION)** — Direct `git push` to GitHub and Render Blueprint deployment cannot execute from this offline build sandbox without your GitHub & Render account authorization.
- **Public Website URL:** **None yet** (not deployed; no fabricated URL claimed).

## 6. Exact Manual Actions Required From You to Go Public (Free on Render)
1. **Push `feat/anveshan-v1-core` to GitHub:** Unzip `ANVESHAN_v1.2_LIVE_DEMO.zip` (or your local repo) and run `bash push_to_github.sh` to push branch `feat/anveshan-v1-core` to [https://github.com/dhundhwana-arch/ANVESHAN](https://github.com/dhundhwana-arch/ANVESHAN).
2. **Deploy Free on Render:** Sign in to Render -> **New +** -> **Blueprint** -> select `dhundhwana-arch/ANVESHAN` (branch `feat/anveshan-v1-core`) -> Render reads `render.yaml` (`plan: free`) and gives you a live `https://anveshan-research-lab.onrender.com` URL.
3. **Optional AI Key:** In Render's Environment tab, add `GEMINI_API_KEY` if you want live AI synthesis enabled (leave blank if you want key-free scientific mode).
