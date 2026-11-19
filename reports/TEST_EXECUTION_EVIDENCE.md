# ANVESHAN v1.2 — Test Execution Evidence

**Project:** ANVESHAN — Advanced Scientific Research & Discovery Platform
**Founder & Developer:** Divyesh Bambhaniya
**Verified Git Branch:** `feat/anveshan-v1-core`
**Verified Commit SHA:** `b73c32c878177cb7c958da6236ad94a93d9e2cc3`
**Verification Date:** 2026-11-19

## Exact Command Executed
```bash
python3 -m unittest discover -s tests -v
```

## Runtime & Dependency Versions
- **Python:** `3.11.2`
- **FastAPI:** `0.92.0`
- **Pydantic:** `1.10.4`
- **NumPy:** `2.1.3`
- **SciPy:** `1.15.2`
- **SymPy:** `1.13.3`
- **Pandas:** `2.2.3`
- **SQLite:** `3.40.1`
- **Note:** `backend/config.py` currently reports `"anveshan": "1.0.0"` in `get_runtime_versions()` (version string was not bumped to `"1.2.0"` in `config.py`).

## Test Summary
- **Total Tests Executed:** 24
- **Passed:** 24
- **Failed:** 0
- **Skipped:** 0
- **Execution Time:** 0.379s
- **Exit Code:** 0

## Verbatim Test Output
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
test_monte_carlo_deterministic_seed (test_math_engine.TestMathEngine.test_monte_carlo_deterministic_seed) ... ok
test_statistics_and_regression_accuracy (test_math_engine.TestMathEngine.test_statistics_and_regression_accuracy) ... ok
test_symbolic_differentiate_and_integrate (test_math_engine.TestMathEngine.test_symbolic_differentiate_and_integrate) ... ok
test_symbolic_security_injection_blocked (test_math_engine.TestMathEngine.test_symbolic_security_injection_blocked) ... ok
test_invalid_physics_parameters_rejected (test_physics_engine.TestPhysicsEngine.test_invalid_physics_parameters_rejected) ... ok
test_oscillator_all_three_damping_regimes (test_physics_engine.TestPhysicsEngine.test_oscillator_all_three_damping_regimes) ... ok
test_projectile_vacuum_matches_analytical_and_drag_reduces_range (test_physics_engine.TestPhysicsEngine.test_projectile_vacuum_matches_analytical_and_drag_reduces_range) ... ok
test_radioactive_decay_half_life_accuracy (test_physics_engine.TestPhysicsEngine.test_radioactive_decay_half_life_accuracy) ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.379s

OK
```

## Known Testing Limitations
1. **Offline Environment:** Live outbound HTTP calls to OpenAlex, arXiv, PubChem, and Google Gemini API cannot execute in this offline build sandbox. Literature response parsers are tested against isolated schema fixtures in `tests/test_literature_engine.py`, and offline `NOT_CONNECTED` / `NOT_CONFIGURED` fallback behavior is tested directly.
2. **Frontend Browser Automation:** No headless browser (Playwright/Selenium) click tests were executed. Frontend HTML serving, required footer attribution, HTTP security headers, and every backing REST endpoint were tested via FastAPI `TestClient`.
3. **Test Runner:** Executed via Python's built-in `unittest` (`pytest` is not pre-installed in the sandbox).
