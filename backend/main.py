from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_runtime_versions, get_settings
from backend.database import Database
from backend.engines.ai_provider import get_ai_provider
from backend.engines.dataset_engine import analyze_csv_dataset
from backend.engines.export_engine import export_literature_bibtex, generate_experiment_markdown_report
from backend.engines.hypothesis_engine import rerun_experiment, verify_hypothesis
from backend.engines.literature_engine import search_literature
from backend.engines.math_engine import (
    run_monte_carlo_pi,
    run_statistical_analysis,
    run_symbolic_operation,
)
from backend.engines.physics_engine import (
    simulate_damped_harmonic_oscillator,
    simulate_projectile_with_drag,
    simulate_logistic_growth,
    simulate_radioactive_decay,
    simulate_thermal_cooling,
)
from backend.models import (
    AIAnalyzeRequest,
    DecayRequest,
    HypothesisCreateRequest,
    HypothesisVerifyRequest,
    LiteratureSearchRequest,
    MonteCarloPiRequest,
    OscillatorRequest,
    ProjectileRequest,
    StatsRequest,
    CSVTextAnalysisRequest,
    CoolingRequest,
    LogisticGrowthRequest,
    SymbolicMathRequest,
)


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app(db_path: Optional[str] = None) -> FastAPI:
    settings = get_settings()
    if db_path is not None:
        settings.db_path = db_path
    db = Database(settings.db_path)

    app = FastAPI(
        title="ANVESHAN — Scientific Research & Discovery Platform",
        description="Real, reproducible scientific computation, literature tracking, and hypothesis falsification engine. Developer by Divyesh Bambhaniya.",
        version="1.2.0",
    )
    app.state.db = db
    app.state.settings = settings

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        )
        return response

    @app.get("/api/system/status")
    def system_status() -> Dict[str, Any]:
        ai = get_ai_provider(get_settings())
        return {
            "platform": "ANVESHAN",
            "subtitle": "Advanced Scientific Research & Discovery Platform",
            "founder": "Divyesh Bambhaniya",
            "status": "OPERATIONAL",
            "database": {"engine": "SQLite", "counts": db.get_counts()},
            "runtime_versions": get_runtime_versions(),
            "ai_provider": ai.status(),
            "scientific_engines": {
                "math_symbolic": "REAL_AND_WORKING",
                "math_statistics": "REAL_AND_WORKING",
                "physics_ode_models": "REAL_AND_WORKING",
                "hypothesis_verification": "REAL_AND_WORKING",
                "literature_apis": "CONFIGURED_REQUIRES_OUTBOUND_NETWORK",
            },
        }

    # --- MATH ENGINE ---
    @app.post("/api/math/symbolic")
    def api_math_symbolic(req: SymbolicMathRequest) -> Dict[str, Any]:
        try:
            params = {
                "expression": req.expression,
                "operation": req.operation,
                "variable": req.variable,
                "lower_bound": req.lower_bound,
                "upper_bound": req.upper_bound,
                "eval_point": req.eval_point,
            }
            output = run_symbolic_operation(**params)
            exp = db.record_experiment(
                domain="math_symbolic",
                research_question=req.research_question,
                methodology=f"SymPy symbolic {req.operation}",
                input_source="user_expression",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/math/statistics")
    def api_math_statistics(req: StatsRequest) -> Dict[str, Any]:
        try:
            params = {
                "x_values": req.x_values,
                "y_values": req.y_values,
                "hypothesized_mean": req.hypothesized_mean,
            }
            output = run_statistical_analysis(**params)
            exp = db.record_experiment(
                domain="math_stats",
                research_question=req.research_question,
                methodology="NumPy/SciPy descriptive stats, normality, t-test & OLS regression",
                input_source="user_dataset",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/math/monte-carlo-pi")
    def api_monte_carlo_pi(req: MonteCarloPiRequest) -> Dict[str, Any]:
        try:
            params = {"samples": req.samples, "seed": req.seed}
            output = run_monte_carlo_pi(**params)
            exp = db.record_experiment(
                domain="monte_carlo_pi",
                research_question=req.research_question,
                methodology="Deterministic seeded Monte Carlo quadrant integration",
                input_source="prng_default_rng",
                parameters=params,
                seed=req.seed,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # --- PHYSICS ENGINE ---
    @app.post("/api/physics/oscillator")
    def api_physics_oscillator(req: OscillatorRequest) -> Dict[str, Any]:
        try:
            params = req.dict(exclude={"research_question"})
            output = simulate_damped_harmonic_oscillator(**params)
            exp = db.record_experiment(
                domain="physics_oscillator",
                research_question=req.research_question,
                methodology="SciPy RK45 ODE integration vs exact analytical solution",
                input_source="deterministic_physical_model",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/physics/projectile")
    def api_physics_projectile(req: ProjectileRequest) -> Dict[str, Any]:
        try:
            params = req.dict(exclude={"research_question"})
            output = simulate_projectile_with_drag(**params)
            exp = db.record_experiment(
                domain="physics_projectile",
                research_question=req.research_question,
                methodology="2D quadratic drag ODE with RK45 event detection vs analytical vacuum limit",
                input_source="deterministic_physical_model",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/physics/decay")
    def api_physics_decay(req: DecayRequest) -> Dict[str, Any]:
        try:
            params = req.dict(exclude={"research_question"})
            output = simulate_radioactive_decay(**params)
            exp = db.record_experiment(
                domain="physics_decay",
                research_question=req.research_question,
                methodology="First-order exponential decay RK45 vs analytical solution",
                input_source="deterministic_physical_model",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/physics/cooling")
    def api_physics_cooling(req: CoolingRequest) -> Dict[str, Any]:
        try:
            params = req.dict(exclude={"research_question"})
            output = simulate_thermal_cooling(**params)
            exp = db.record_experiment(
                domain="physics_cooling",
                research_question=req.research_question,
                methodology="Newton's law of cooling RK45 vs analytical exponential convergence",
                input_source="deterministic_physical_model",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/physics/logistic")
    def api_physics_logistic(req: LogisticGrowthRequest) -> Dict[str, Any]:
        try:
            params = req.dict(exclude={"research_question"})
            output = simulate_logistic_growth(**params)
            exp = db.record_experiment(
                domain="physics_logistic",
                research_question=req.research_question,
                methodology="Logistic growth ODE RK45 vs exact analytical sigmoid",
                input_source="deterministic_physical_model",
                parameters=params,
                software_versions=get_runtime_versions(),
                epistemic_label="COMPUTATIONAL_RESULT",
                status="COMPLETED",
                output=output,
            )
            return {"experiment": exp, "result": output}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # --- DATASET ANALYSIS WORKBENCH ---
    @app.post("/api/datasets/analyze")
    def api_analyze_dataset(req: CSVTextAnalysisRequest) -> Dict[str, Any]:
        try:
            result = analyze_csv_dataset(
                req.csv_text.encode("utf-8"),
                filename=req.filename,
                x_col=req.x_col or None,
                y_col=req.y_col or None,
            )
            ds = db.record_dataset(
                filename=result["filename"],
                checksum_sha256=result["checksum_sha256"],
                row_count=result["row_count"],
                col_count=result["col_count"],
                columns=result["columns"],
            )
            exp = db.record_experiment(
                domain="dataset_analysis",
                research_question=req.research_question,
                methodology="Pandas/SciPy CSV descriptive statistics, Pearson correlation & OLS regression",
                input_source=f"csv:{result['filename']} (sha256:{result['checksum_sha256'][:12]})",
                parameters={"filename": result["filename"], "x_col": req.x_col, "y_col": req.y_col, "dataset_checksum": result["checksum_sha256"]},
                software_versions=get_runtime_versions(),
                epistemic_label="OBSERVED_DATA",
                status="COMPLETED",
                output=result,
            )
            return {"dataset": ds, "experiment": exp, "result": result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/api/datasets")
    def api_list_datasets(limit: int = 50) -> Dict[str, Any]:
        items = db.list_datasets(limit=max(1, min(limit, 200)))
        return {"count": len(items), "datasets": items}

    # --- LITERATURE ENGINE ---
    @app.post("/api/literature/search")
    def api_literature_search(req: LiteratureSearchRequest) -> Dict[str, Any]:
        try:
            res = search_literature(req.query, req.provider, req.limit, get_settings())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        saved = []
        if req.save_results and res.get("status") == "CONNECTED":
            for rec in res["results"]:
                saved.append(db.save_literature_source(rec))
        res["saved_count"] = len(saved)
        return res

    @app.get("/api/literature/library")
    def api_literature_library(limit: int = 50) -> Dict[str, Any]:
        items = db.list_literature_sources(limit=max(1, min(limit, 200)))
        return {"count": len(items), "sources": items}

    @app.get("/api/literature/export/bibtex", response_class=PlainTextResponse)
    def api_literature_bibtex() -> str:
        return export_literature_bibtex(db.list_literature_sources(limit=200))

    # --- HYPOTHESIS & VERIFICATION ENGINE ---
    @app.post("/api/hypotheses")
    def api_create_hypothesis(req: HypothesisCreateRequest) -> Dict[str, Any]:
        allowed_domains = {"physics_oscillator", "physics_projectile", "physics_decay", "physics_cooling", "physics_logistic", "math_stats", "monte_carlo_pi"}
        if req.test_domain not in allowed_domains:
            raise HTTPException(status_code=400, detail=f"Unsupported test_domain. Allowed: {sorted(allowed_domains)}")
        if "metric" not in req.acceptance_criteria or "target" not in req.acceptance_criteria:
            raise HTTPException(status_code=400, detail="acceptance_criteria must include 'metric' and 'target'.")
        return db.create_hypothesis(
            title=req.title,
            statement=req.statement,
            assumptions=req.assumptions,
            falsifiable_prediction=req.falsifiable_prediction,
            test_domain=req.test_domain,
            test_config=req.test_config,
            acceptance_criteria=req.acceptance_criteria,
        )

    @app.get("/api/hypotheses")
    def api_list_hypotheses(limit: int = 50) -> Dict[str, Any]:
        items = db.list_hypotheses(limit=max(1, min(limit, 200)))
        return {"count": len(items), "hypotheses": items}

    @app.get("/api/hypotheses/{hypothesis_id}")
    def api_get_hypothesis(hypothesis_id: str) -> Dict[str, Any]:
        hyp = db.get_hypothesis(hypothesis_id)
        if not hyp:
            raise HTTPException(status_code=404, detail="Hypothesis not found.")
        return hyp

    @app.post("/api/hypotheses/{hypothesis_id}/verify")
    def api_verify_hypothesis(hypothesis_id: str, req: HypothesisVerifyRequest = HypothesisVerifyRequest()) -> Dict[str, Any]:
        try:
            return verify_hypothesis(db, hypothesis_id, seed=req.seed)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    # --- EXPERIMENTS & REPRODUCIBILITY ---
    @app.get("/api/experiments")
    def api_list_experiments(limit: int = 50, domain: Optional[str] = None) -> Dict[str, Any]:
        items = db.list_experiments(limit=max(1, min(limit, 200)), domain=domain)
        return {"count": len(items), "experiments": items}

    @app.get("/api/experiments/{experiment_id}")
    def api_get_experiment(experiment_id: str) -> Dict[str, Any]:
        exp = db.get_experiment(experiment_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        return exp

    @app.post("/api/experiments/{experiment_id}/rerun")
    def api_rerun_experiment(experiment_id: str) -> Dict[str, Any]:
        try:
            return rerun_experiment(db, experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/api/experiments/{experiment_id}/report", response_class=PlainTextResponse)
    def api_experiment_report(experiment_id: str) -> str:
        exp = db.get_experiment(experiment_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        return generate_experiment_markdown_report(exp)

    # --- AI SYNTHESIS (OPTIONAL, REPLACEABLE) ---
    @app.post("/api/ai/analyze")
    def api_ai_analyze(req: AIAnalyzeRequest) -> Dict[str, Any]:
        ai = get_ai_provider(get_settings())
        try:
            return ai.analyze(req.prompt, req.context)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # --- FRONTEND SERVING ---
    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

        @app.get("/")
        def serve_index():
            return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.exception_handler(Exception)
    async def safe_exception_handler(_request: Request, _exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Check server logs for diagnostics."},
        )

    return app


app = create_app()
