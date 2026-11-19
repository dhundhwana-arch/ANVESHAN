# ANVESHAN
Open-source Scientific Research & Discovery Platform (v1.2).

**Founder & Developer:** Divyesh Bambhaniya
**Repository:** [https://github.com/dhundhwana-arch/ANVESHAN](https://github.com/dhundhwana-arch/ANVESHAN)
**License:** MIT (`LICENSE`)

## Actual Implemented Features (v1.2)
All backend engines live under `backend/engines/` and are exposed through FastAPI (`backend/main.py`) with SQLite persistence (`backend/database.py`):

1. **Mathematical Engine (`backend/engines/math_engine.py`):** Safe SymPy symbolic operations (`simplify`, `differentiate`, `integrate`, `solve`, `expand`, `factor`) with restricted parser sandbox; NumPy/SciPy descriptive statistics, Shapiro-Wilk normality test, one-sample t-test, OLS linear regression (with correlation-vs-causation warning), and seeded Monte Carlo Pi estimation.
2. **Physics Simulation Engine (`backend/engines/physics_engine.py`):** Deterministic SciPy RK45 ODE solvers verified against closed-form analytical solutions:
   - Damped Harmonic Oscillator (underdamped, critically damped, overdamped + energy check)
   - 2D Projectile Motion with Quadratic Air Drag (vs analytical vacuum range)
   - First-Order Radioactive Decay
   - Newton's Law of Thermal Cooling
   - Logistic Population Growth
3. **Immutable Experiment Ledger (`backend/database.py`):** SQLite database with `BEFORE UPDATE` and `BEFORE DELETE` triggers preventing silent historical modification, SHA-256 parameter checksums, runtime version capture, and deterministic reruns (`POST /api/experiments/{id}/rerun`).
4. **Hypothesis Verification Engine (`backend/engines/hypothesis_engine.py`):** Stores explicit assumptions, falsifiable predictions, and acceptance criteria; executes real computational tests and records both `SUPPORTED_BY_COMPUTATION` and `FALSIFIED_BY_COMPUTATION` (`FAILED_EXPERIMENT`) outcomes.
5. **CSV Data Analysis Workbench (`backend/engines/dataset_engine.py`):** Parses CSV data (up to 2 MB) via Pandas, computes SHA-256 dataset checksums, missing-value counts, per-column descriptive statistics, Pearson correlation matrices, and OLS linear regression.
6. **Evidence Exports (`backend/engines/export_engine.py`):** BibTeX citation export from saved SQLite literature records (`GET /api/literature/export/bibtex`) and downloadable Markdown experiment evidence reports (`GET /api/experiments/{id}/report`).
7. **Scientific Literature Clients (`backend/engines/literature_engine.py`):** HTTP clients for [OpenAlex](https://help.openalex.org/api/), [arXiv](https://info.arxiv.org/help/api/user-manual.html), and [PubChem PUG-REST](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030920/) with rate-limit guards and honest `NOT_CONNECTED` reporting when offline.
8. **Replaceable AI Synthesis Adapter (`backend/engines/ai_provider.py`):** Google [Gemini API](https://aistudio.google.com/api-reference) REST adapter via `GEMINI_API_KEY`. Core scientific engines work 100% without an AI key.
9. **Research Lab Web UI (`frontend/`):** Responsive dark-obsidian HTML/CSS/JS interface with 7 workspace tabs and Canvas plots.

## Installation & Running

### Linux / macOS
```bash
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Android Termux
```bash
pkg update && pkg install python git
cp .env.example .env
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*(Note: Installing SciPy/NumPy via `pip` on Termux may require `pkg install python-numpy python-scipy` depending on Android architecture.)*

## API Configuration (Optional)
Copy `.env.example` to `.env` (never commit `.env`):
- `GEMINI_API_KEY`: Optional key from [Google AI Studio](https://aistudio.google.com/docs/api-key) for `/api/ai/analyze`.
- `OPENALEX_EMAIL` / `OPENALEX_API_KEY`: Optional polite-pool email or key from [OpenAlex Authentication Docs](https://help.openalex.org/api/authentication/).
- `ANVESHAN_DB_PATH`: SQLite file path (default `./data/anveshan.db`).

## Known Limitations (Honest Audit Disclosure)
- **External APIs Not Live-Tested in Build Sandbox:** OpenAlex, arXiv, PubChem, and Gemini HTTP clients were verified offline (schema parsers + `NOT_CONNECTED`/`NOT_CONFIGURED` handling) and must be verified on a networked host.
- **No Browser E2E Automation Yet:** Backend APIs and HTML serving are tested via FastAPI `TestClient` (24/24 passing), but headless browser click/layout tests have not yet been run.
- **Single-User Local/Private Scope:** No multi-user authentication (JWT/OAuth) is implemented yet.
- **Not Yet Deployed / Not Yet Pushed:** Upstream GitHub `main` remains at `3451505` until pushed by the repository owner; Render deployment (`render.yaml`) has not been executed.

## Attribution
**ANVESHAN — Advanced Scientific Research & Discovery Platform**
**Founder & Developer:** Divyesh Bambhaniya
*Developer by Divyesh Bambhaniya*
