from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SymbolicMathRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=300)
    operation: str = Field("simplify")
    variable: str = Field("x", max_length=4)
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    eval_point: Optional[float] = None
    research_question: str = Field("Symbolic mathematical evaluation", max_length=400)


class StatsRequest(BaseModel):
    x_values: List[float] = Field(..., min_items=2, max_items=5000)
    y_values: Optional[List[float]] = None
    hypothesized_mean: Optional[float] = None
    research_question: str = Field("Statistical analysis", max_length=400)


class MonteCarloPiRequest(BaseModel):
    samples: int = Field(10000, ge=100, le=500000)
    seed: int = Field(42)
    research_question: str = Field("Deterministic Monte Carlo estimation of Pi", max_length=400)


class OscillatorRequest(BaseModel):
    mass_kg: float = Field(1.0, gt=0)
    damping_ns_per_m: float = Field(0.4, ge=0)
    stiffness_n_per_m: float = Field(4.0, gt=0)
    x0_m: float = Field(1.0)
    v0_m_per_s: float = Field(0.0)
    duration_s: float = Field(12.0, ge=0.1, le=200.0)
    num_points: int = Field(160, ge=20, le=1000)
    research_question: str = Field("Damped harmonic oscillator RK45 vs analytical comparison", max_length=400)


class ProjectileRequest(BaseModel):
    v0_m_per_s: float = Field(40.0, gt=0)
    angle_deg: float = Field(45.0, ge=1.0, le=89.0)
    mass_kg: float = Field(0.145, gt=0)
    drag_coeff: float = Field(0.47, ge=0)
    area_m2: float = Field(0.0042, ge=0)
    air_density_kg_m3: float = Field(1.225, ge=0)
    gravity_m_s2: float = Field(9.80665, gt=0)
    research_question: str = Field("2D projectile trajectory with quadratic air drag", max_length=400)


class DecayRequest(BaseModel):
    n0: float = Field(1000.0, gt=0)
    half_life_s: float = Field(10.0, gt=0)
    duration_s: float = Field(50.0, gt=0)
    num_points: int = Field(100, ge=20, le=1000)
    research_question: str = Field("First-order radioactive decay verification", max_length=400)


class LiteratureSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    provider: str = Field("openalex")
    limit: int = Field(5, ge=1, le=20)
    save_results: bool = Field(True)


class HypothesisCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    statement: str = Field(..., min_length=5, max_length=1000)
    assumptions: List[str] = Field(..., min_items=1)
    falsifiable_prediction: str = Field(..., min_length=5, max_length=500)
    test_domain: str = Field(...)
    test_config: Dict[str, Any] = Field(...)
    acceptance_criteria: Dict[str, Any] = Field(...)


class HypothesisVerifyRequest(BaseModel):
    seed: Optional[int] = None


class AIAnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=2000)
    context: str = Field("", max_length=4000)


class CoolingRequest(BaseModel):
    t0_c: float = Field(90.0)
    t_env_c: float = Field(22.0)
    cooling_k_per_s: float = Field(0.05, gt=0)
    duration_s: float = Field(120.0, gt=0, le=5000.0)
    num_points: int = Field(120, ge=20, le=1000)
    research_question: str = Field("Newton's law of thermal cooling ODE verification", max_length=400)


class LogisticGrowthRequest(BaseModel):
    p0: float = Field(10.0, gt=0)
    carrying_capacity_k: float = Field(1000.0, gt=0)
    growth_rate_r: float = Field(0.25, gt=0)
    duration_t: float = Field(40.0, gt=0, le=500.0)
    num_points: int = Field(120, ge=20, le=1000)
    research_question: str = Field("Logistic population growth ODE vs analytical verification", max_length=400)


class CSVTextAnalysisRequest(BaseModel):
    filename: str = Field("dataset.csv", max_length=120)
    csv_text: str = Field(..., min_length=3, max_length=2000000)
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    research_question: str = Field("Tabular CSV dataset statistical & correlation analysis", max_length=400)
