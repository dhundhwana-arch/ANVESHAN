# ANVESHAN — Final Test Report

## Exact Execution Command
```bash
python3 -m unittest discover -s tests -v
```

## Execution Summary
- **Status:** PASSED
- **Total Executed:** 19
- **Passed:** 19
- **Failed:** 0
- **Skipped:** 0
- **Runtime:** ~0.33s (Python 3.11.2, FastAPI 0.92.0, NumPy 2.1.3, SciPy 1.15.2, SymPy 1.13.3)

## Defects Discovered & Fixed During Testing
1. `backend/engines/ai_provider.py` — Unescaped newline inside string literal caused `SyntaxError` on import; fixed in commit `38f5413`.
2. `backend/engines/math_engine.py` — Empty `global_dict` omitted SymPy numeric constructors (`Integer`, `Float`, `Symbol`, `Rational`) needed by `parse_expr`; fixed in commit `38f5413` while preserving `__builtins__: {}` isolation.

## Known Testing Limitations
- Live outbound HTTP calls to OpenAlex, arXiv, PubChem, and Google Gemini API could not execute inside the offline build sandbox; schema parsers were verified with explicitly labeled test fixtures, and offline `NOT_CONNECTED` / `NOT_CONFIGURED` error handling was verified directly.
- Headless browser DOM click automation (Playwright/Selenium) was not executed; frontend HTML delivery, brand footer, security headers, and every backing API endpoint were verified via FastAPI `TestClient`.
