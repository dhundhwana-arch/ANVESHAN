# ANVESHAN — System Architecture

**Project:** ANVESHAN — Advanced Scientific Research & Discovery Platform
**Founder & Developer:** Divyesh Bambhaniya

## 1. Design Principles
1. **Zero Fake Functionality:** Every API endpoint runs real mathematical, physical, database, or external HTTP logic. Missing credentials or offline networks return explicit structured status codes (`NOT_CONNECTED`, `NOT_CONFIGURED`) rather than synthetic outputs.
2. **Epistemic Integrity:** Records explicitly tag epistemic status: `ESTABLISHED_KNOWLEDGE`, `OBSERVED_DATA`, `COMPUTATIONAL_RESULT`, `PROPOSED_HYPOTHESIS`, `UNVERIFIED_CLAIM`, `FAILED_EXPERIMENT`, `UNRESOLVED_QUESTION`.
3. **Append-Only Experimental Ledger:** Experiment runs are never silently mutated; reruns create linked child records referencing `parent_experiment_id` with SHA-256 input/parameter checksums and exact library versions.
4. **Tablet & Termux Friendly:** Lightweight Python 3.11 + FastAPI + SQLite + NumPy/SciPy/SymPy backend with a zero-build responsive HTML5/CSS3/JS frontend (no heavy Node toolchain required to run).

## 2. Layered Vertical Architecture
```
[Browser / Android Tablet / Desktop UI] (frontend/index.html, styles.css, app.js)
        │  Real HTTP/JSON via fetch()
        ▼
[FastAPI Application Layer] (backend/main.py, backend/models.py)
  ├─ Input Validation (Pydantic) & Security Headers Middleware
  ├─ /api/system/status     -> Real runtime versions, DB health, AI/API readiness
  ├─ /api/math/*            -> Math Engine (SymPy symbolic + NumPy/SciPy stats)
  ├─ /api/physics/*         -> Physics Engine (SciPy RK45 ODE + analytical comparison)
  ├─ /api/literature/*      -> OpenAlex, arXiv, PubChem HTTP clients + SQLite library
  ├─ /api/hypotheses/*      -> Falsifiable hypothesis store + automated computational tests
  ├─ /api/experiments/*     -> Immutable experiment history, checksums, deterministic reruns
  └─ /api/ai/*              -> Replaceable Gemini API adapter (honest status if unconfigured)
        │
        ▼
[SQLite Persistence Layer] (backend/database.py)
  ├─ experiments            (immutable run ledger, parameters JSON, outputs JSON, checksum, seed, env versions)
  ├─ literature_sources     (real metadata, DOI/arXiv/CID, URLs, abstract vs full-text flag)
  ├─ hypotheses             (assumptions, falsifiable predictions, acceptance criteria, status)
  └─ verification_runs      (links hypothesis_id <-> experiment_id, pass/fail evaluation)
```

## 3. Verified External API Specifications
- **OpenAlex API:** [Official Docs](https://help.openalex.org/api/) — Base `https://api.openalex.org/works`; [Rate Limits](https://github.com/ourresearch/openalex-docs/blob/main/how-to-use-the-api/rate-limits-and-authentication.md): 100,000 credits/day free tier, max 100 req/s; supports optional `mailto` / `api_key`.
- **arXiv API:** [User's Manual](https://info.arxiv.org/help/api/user-manual.html) — Base `https://export.arxiv.org/api/query` returning Atom XML; [Terms of Use](https://info.arxiv.org/help/api/tou.html): max 1 request per 3 seconds, single connection.
- **PubChem PUG-REST:** [NIH/PMC Documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030920/) — Base `https://pubchem.ncbi.nlm.nih.gov/rest/pug`; max 5 req/s and 400 req/min, keyless.
- **Google Gemini API:** [API Reference](https://aistudio.google.com/api-reference) — REST `generateContent` endpoint authenticated via `GEMINI_API_KEY` environment variable (never exposed to frontend).
