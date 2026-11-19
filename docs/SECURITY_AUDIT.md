# ANVESHAN — Security Audit

1. **Secrets Hygiene:** Zero API keys, tokens, or passwords committed. `.env` is excluded in `.gitignore`; `.env.example` contains placeholder variable names only.
2. **Frontend Isolation:** `GEMINI_API_KEY` and `OPENALEX_API_KEY` are read exclusively on the Python backend (`backend/config.py`) and never returned in any API payload or frontend asset.
3. **Code Injection Prevention (SymPy):** `safe_parse_expression` enforces a 300-char limit, blocks dunder/builtin tokens (`__`, `import`, `exec`, `eval`, `open`, `lambda`, `os.`, `sys.`, `subprocess`), and uses a restricted `global_dict` containing only `{"__builtins__": {}, "Integer": ..., "Float": ..., "Symbol": ..., "Rational": ...}`. Verified by `test_symbolic_security_injection_blocked`.
4. **SQL Injection Prevention:** All SQLite queries use parameterized `?` bindings exclusively.
5. **HTTP Security Headers:** Middleware attaches `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and `Content-Security-Policy`. Verified by `test_api_e2e.py`.
6. **Input Validation & Safe Error Handling:** Pydantic models enforce strict numeric bounds; global 500 handler suppresses raw stack traces.
7. **Known Security Limitations:** No multi-user authentication (JWT/OAuth) is enabled in v1.0 because ANVESHAN v1.0 is designed as a single-researcher local/Termux or private Render instance. Before opening to multi-user public traffic, add authentication and rate limiting.
