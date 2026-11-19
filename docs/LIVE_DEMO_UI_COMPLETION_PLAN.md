# ANVESHAN v1.2.0 — Live Demo UI Completion Plan & Status

**Branch:** `feat/anveshan-v1-core`
**Status:** Core Live Demo UI controls were wired in commit `74b6fbc`; remaining minor UI gaps are documented below.

| Workspace Tab | Required Controls | Backend Endpoint(s) | Current UI Status | Remaining Gap |
| --- | --- | --- | --- | --- |
| Mathematical Lab | Symbolic Calculus/Solve, Statistics/OLS, Monte Carlo Pi | `POST /api/math/symbolic`, `/api/math/statistics`, `/api/math/monte-carlo-pi` | **Wired & Tested** (`74b6fbc`) | Add optional definite integral lower/upper bound inputs in UI form. |
| Physics Lab | Oscillator, Projectile w/ Drag, Radioactive Decay, Thermal Cooling, Logistic Growth | `POST /api/physics/oscillator`, `/projectile`, `/decay`, `/cooling`, `/logistic` | **Wired & Tested** (`74b6fbc`) | Real browser/tablet visual verification pending local/hosted run. |
| Hypothesis Lab | Assumptions, predictions, all operators (`<=,<,>=,>,approx`), domains | `POST /api/hypotheses`, `POST /api/hypotheses/{id}/verify` | **Mostly Wired** (`74b6fbc`) | Add `math_stats` option to the Hypothesis UI domain selector (currently has 6 domains; `math_stats` works via API). |
| Experiment Ledger | Experiment ID, SHA-256 checksum, Rerun & Verify, Markdown `.md` report download | `GET /api/experiments`, `POST /api/experiments/{id}/rerun`, `GET /api/experiments/{id}/report` | **Wired & Tested** (`74b6fbc`) | Display `output_checksum` alongside `input_checksum` in ledger item card. |
