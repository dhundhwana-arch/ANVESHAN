from typing import Any, Dict, Optional, Tuple

from backend.config import get_runtime_versions
from backend.database import Database
from backend.engines.math_engine import run_monte_carlo_pi, run_statistical_analysis
from backend.engines.physics_engine import (
    simulate_damped_harmonic_oscillator,
    simulate_projectile_with_drag,
    simulate_logistic_growth,
    simulate_radioactive_decay,
    simulate_thermal_cooling,
)


def _extract_nested_metric(data: Dict[str, Any], path: str) -> float:
    curr: Any = data
    for key in path.split("."):
        if isinstance(curr, dict) and key in curr:
            curr = curr[key]
        else:
            raise KeyError(f"Metric path '{path}' not found in experiment output.")
    if not isinstance(curr, (int, float)):
        raise ValueError(f"Metric '{path}' is not numeric: {type(curr).__name__}")
    return float(curr)


def evaluate_criterion(observed: float, criteria: Dict[str, Any]) -> Tuple[bool, str]:
    op = criteria.get("operator", "<=")
    target = float(criteria["target"])
    tol = float(criteria.get("tolerance", 1e-3))

    if op == "<":
        return observed < target, f"observed ({observed:.6g}) < {target:.6g}"
    if op == "<=":
        return observed <= target, f"observed ({observed:.6g}) <= {target:.6g}"
    if op == ">":
        return observed > target, f"observed ({observed:.6g}) > {target:.6g}"
    if op == ">=":
        return observed >= target, f"observed ({observed:.6g}) >= {target:.6g}"
    if op == "approx":
        return abs(observed - target) <= tol, f"|observed ({observed:.6g}) - {target:.6g}| <= {tol:.6g}"
    raise ValueError(f"Unsupported acceptance operator '{op}'. Allowed: <, <=, >, >=, approx.")


def execute_domain_computation(domain: str, config: Dict[str, Any], seed: Optional[int] = None) -> Dict[str, Any]:
    if domain == "physics_oscillator":
        return simulate_damped_harmonic_oscillator(**config)
    if domain == "physics_projectile":
        return simulate_projectile_with_drag(**config)
    if domain == "physics_decay":
        return simulate_radioactive_decay(**config)
    if domain == "physics_cooling":
        return simulate_thermal_cooling(**config)
    if domain == "physics_logistic":
        return simulate_logistic_growth(**config)
    if domain == "math_stats":
        return run_statistical_analysis(**config)
    if domain == "monte_carlo_pi":
        cfg = dict(config)
        if seed is not None:
            cfg["seed"] = seed
        return run_monte_carlo_pi(**cfg)
    raise ValueError(
        f"Unsupported test_domain '{domain}'. Supported: physics_oscillator, physics_projectile, physics_decay, math_stats, monte_carlo_pi."
    )


def verify_hypothesis(db: Database, hypothesis_id: str, seed: Optional[int] = None) -> Dict[str, Any]:
    hyp = db.get_hypothesis(hypothesis_id)
    if not hyp:
        raise KeyError(f"Hypothesis '{hypothesis_id}' not found.")

    domain = hyp["test_domain"]
    config = hyp["test_config"]
    criteria = hyp["acceptance_criteria"]
    effective_seed = seed if seed is not None else config.get("seed")

    try:
        output = execute_domain_computation(domain, config, seed=effective_seed)
        metric_path = criteria["metric"]
        observed = _extract_nested_metric(output, metric_path)
        passed, desc = evaluate_criterion(observed, criteria)

        exp = db.record_experiment(
            domain=domain,
            research_question=f"Hypothesis Test [{hyp['id']}]: {hyp['statement']}",
            methodology=f"Automated computational falsification test on {domain}",
            input_source=f"hypothesis:{hyp['id']}",
            parameters=config,
            seed=effective_seed,
            software_versions=get_runtime_versions(),
            epistemic_label="COMPUTATIONAL_RESULT" if passed else "FAILED_EXPERIMENT",
            status="COMPLETED",
            output=output,
        )

        new_status = "SUPPORTED_BY_COMPUTATION" if passed else "FALSIFIED_BY_COMPUTATION"
        summary = (
            f"Criterion PASSED ({desc}). Computational test supports prediction under stated assumptions; does NOT constitute universal proof."
            if passed
            else f"Criterion FAILED ({desc}). Prediction was falsified under stated parameters; failed run preserved in ledger."
        )
        ver = db.record_verification_run(
            hypothesis_id=hyp["id"],
            experiment_id=exp["id"],
            passed=passed,
            observed_value=observed,
            threshold_description=f"{metric_path}: {desc}",
            evaluation_summary=summary,
            new_epistemic_status=new_status,
        )
        return {"verification": ver, "experiment": exp}

    except Exception as exc:
        exp = db.record_experiment(
            domain=domain,
            research_question=f"Hypothesis Test [{hyp['id']}]: {hyp['statement']}",
            methodology=f"Automated computational falsification test on {domain}",
            input_source=f"hypothesis:{hyp['id']}",
            parameters=config,
            seed=effective_seed,
            software_versions=get_runtime_versions(),
            epistemic_label="FAILED_EXPERIMENT",
            status="FAILED",
            output=None,
            error_message=str(exc),
        )
        ver = db.record_verification_run(
            hypothesis_id=hyp["id"],
            experiment_id=exp["id"],
            passed=False,
            observed_value=None,
            threshold_description=str(criteria),
            evaluation_summary=f"Execution failed with error: {exc}",
            new_epistemic_status="FAILED_EXPERIMENT",
        )
        return {"verification": ver, "experiment": exp}


def _max_numeric_diff(a: Any, b: Any) -> float:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b))
    if isinstance(a, dict) and isinstance(b, dict):
        diffs = [_max_numeric_diff(a[k], b[k]) for k in a.keys() if k in b]
        return max(diffs) if diffs else 0.0
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        diffs = [_max_numeric_diff(x, y) for x, y in zip(a, b)]
        return max(diffs) if diffs else 0.0
    return 0.0


def rerun_experiment(db: Database, experiment_id: str) -> Dict[str, Any]:
    original = db.get_experiment(experiment_id)
    if not original:
        raise KeyError(f"Experiment '{experiment_id}' not found.")

    domain = original["domain"]
    params = original["parameters"]
    seed = original["seed"]

    if domain == "math_symbolic":
        from backend.engines.math_engine import run_symbolic_operation
        output = run_symbolic_operation(**params)
    else:
        output = execute_domain_computation(domain, params, seed=seed)

    rerun = db.record_experiment(
        domain=domain,
        research_question=original["research_question"],
        methodology=f"Reproducibility rerun of {original['id']}",
        input_source=f"rerun:{original['id']}",
        parameters=params,
        seed=seed,
        software_versions=get_runtime_versions(),
        epistemic_label="COMPUTATIONAL_RESULT",
        status="COMPLETED",
        output=output,
        parent_experiment_id=original["id"],
    )

    max_diff = _max_numeric_diff(original.get("output"), output)
    checksum_match = original["input_checksum"] == rerun["input_checksum"]
    output_checksum_match = (
        original.get("output_checksum") == rerun.get("output_checksum")
        if original.get("output_checksum") is not None
        else None
    )
    reproducible = bool(
        checksum_match
        and max_diff <= 1e-12
        and (output_checksum_match is None or output_checksum_match)
    )

    return {
        "original_experiment_id": original["id"],
        "rerun_experiment": rerun,
        "checksum_match": checksum_match,
        "output_checksum_match": output_checksum_match,
        "max_numeric_diff": max_diff,
        "reproducible": reproducible,
    }
