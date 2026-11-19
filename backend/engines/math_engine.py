import re
from typing import Any, Dict, List, Optional

import numpy as np
import sympy as sp
from scipy import stats
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


FORBIDDEN_PATTERNS = re.compile(
    r"(__|import|exec|eval|open|lambda|os\.|sys\.|subprocess|getattr|setattr|delattr|globals|locals)",
    re.IGNORECASE,
)

ALLOWED_SYMBOLS = {
    "x": sp.Symbol("x", real=True),
    "y": sp.Symbol("y", real=True),
    "z": sp.Symbol("z", real=True),
    "t": sp.Symbol("t", real=True),
    "n": sp.Symbol("n", real=True),
    "k": sp.Symbol("k", real=True),
    "a": sp.Symbol("a", real=True),
    "b": sp.Symbol("b", real=True),
    "c": sp.Symbol("c", real=True),
    "pi": sp.pi,
    "E": sp.E,
    "e": sp.E,
    "oo": sp.oo,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "Abs": sp.Abs,
    "abs": sp.Abs,
    "Rational": sp.Rational,
    "factorial": sp.factorial,
}

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def safe_parse_expression(expression: str) -> sp.Expr:
    cleaned = expression.strip()
    if not cleaned:
        raise ValueError("Expression must not be empty.")
    if len(cleaned) > 300:
        raise ValueError("Expression exceeds maximum allowed length (300 characters).")
    if FORBIDDEN_PATTERNS.search(cleaned):
        raise ValueError("Expression contains disallowed tokens.")
    try:
        expr = parse_expr(
            cleaned,
            local_dict=ALLOWED_SYMBOLS,
            global_dict={"__builtins__": {}, "Integer": sp.Integer, "Float": sp.Float, "Symbol": sp.Symbol, "Rational": sp.Rational},
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as exc:
        raise ValueError(f"Could not parse mathematical expression: {exc}") from exc
    if not isinstance(expr, sp.Basic):
        raise ValueError("Parsed result is not a valid symbolic mathematical expression.")
    return expr


def run_symbolic_operation(
    expression: str,
    operation: str = "simplify",
    variable: str = "x",
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None,
    eval_point: Optional[float] = None,
) -> Dict[str, Any]:
    if variable not in {"x", "y", "z", "t", "n", "k", "a", "b", "c"}:
        raise ValueError(f"Unsupported variable '{variable}'. Allowed: x, y, z, t, n, k, a, b, c.")

    expr = safe_parse_expression(expression)
    sym = ALLOWED_SYMBOLS[variable]
    op = operation.lower().strip()

    if op == "simplify":
        result_expr = sp.simplify(expr)
        result_str = str(result_expr)
        result_latex = sp.latex(result_expr)
    elif op == "differentiate":
        result_expr = sp.diff(expr, sym)
        result_str = str(result_expr)
        result_latex = sp.latex(result_expr)
    elif op == "integrate":
        if lower_bound is not None and upper_bound is not None:
            result_expr = sp.integrate(expr, (sym, lower_bound, upper_bound))
        else:
            result_expr = sp.integrate(expr, sym)
        result_str = str(result_expr)
        result_latex = sp.latex(result_expr)
    elif op == "solve":
        solutions = sp.solve(expr, sym)
        result_expr = solutions
        result_str = ", ".join(str(s) for s in solutions) if solutions else "No symbolic solution found"
        result_latex = sp.latex(solutions)
    elif op == "expand":
        result_expr = sp.expand(expr)
        result_str = str(result_expr)
        result_latex = sp.latex(result_expr)
    elif op == "factor":
        result_expr = sp.factor(expr)
        result_str = str(result_expr)
        result_latex = sp.latex(result_expr)
    else:
        raise ValueError(
            f"Unsupported operation '{operation}'. Supported: simplify, differentiate, integrate, solve, expand, factor."
        )

    numerical_value: Optional[float] = None
    if eval_point is not None and isinstance(result_expr, sp.Basic):
        evaluated = result_expr.subs(sym, eval_point).evalf()
        if evaluated.is_real:
            numerical_value = float(evaluated)
    elif isinstance(result_expr, sp.Basic) and not result_expr.free_symbols:
        evaluated = result_expr.evalf()
        if evaluated.is_real:
            numerical_value = float(evaluated)

    # Sample curve points for real visualization when expression is univariate
    plot_points: List[Dict[str, float]] = []
    if isinstance(expr, sp.Basic) and expr.free_symbols.issubset({sym}):
        xs = np.linspace(-5.0, 5.0, 61)
        f_orig = sp.lambdify(sym, expr, modules=["numpy"])
        f_res = (
            sp.lambdify(sym, result_expr, modules=["numpy"])
            if isinstance(result_expr, sp.Basic) and result_expr.free_symbols.issubset({sym})
            else None
        )
        for xv in xs:
            try:
                yv = float(np.real(f_orig(float(xv))))
                if not np.isfinite(yv) or abs(yv) > 1e6:
                    continue
                pt: Dict[str, float] = {"x": round(float(xv), 4), "input_y": round(yv, 6)}
                if f_res is not None:
                    ry = float(np.real(f_res(float(xv))))
                    if np.isfinite(ry) and abs(ry) <= 1e6:
                        pt["result_y"] = round(ry, 6)
                plot_points.append(pt)
            except Exception:
                continue

    return {
        "input_expression": str(expr),
        "input_latex": sp.latex(expr),
        "operation": op,
        "variable": variable,
        "result": result_str,
        "result_latex": result_latex,
        "numerical_value": numerical_value,
        "plot_points": plot_points,
        "epistemic_note": "Computed symbolically using SymPy; numerical samples are evaluated directly from the parsed expression.",
    }


def run_statistical_analysis(
    x_values: List[float],
    y_values: Optional[List[float]] = None,
    hypothesized_mean: Optional[float] = None,
) -> Dict[str, Any]:
    if len(x_values) < 2:
        raise ValueError("At least 2 numeric observations are required in x_values.")
    arr_x = np.asarray(x_values, dtype=float)
    if not np.all(np.isfinite(arr_x)):
        raise ValueError("x_values must contain only finite real numbers.")

    q25, q50, q75 = np.percentile(arr_x, [25, 50, 75])
    descriptive = {
        "n": int(arr_x.size),
        "mean": float(np.mean(arr_x)),
        "median": float(q50),
        "std_sample": float(np.std(arr_x, ddof=1)),
        "std_population": float(np.std(arr_x, ddof=0)),
        "variance_sample": float(np.var(arr_x, ddof=1)),
        "min": float(np.min(arr_x)),
        "max": float(np.max(arr_x)),
        "iqr": float(q75 - q25),
        "skewness": float(stats.skew(arr_x)),
        "kurtosis_excess": float(stats.kurtosis(arr_x)),
    }

    normality: Optional[Dict[str, Any]] = None
    if 3 <= arr_x.size <= 5000 and float(np.ptp(arr_x)) > 0.0:
        w_stat, p_val = stats.shapiro(arr_x)
        normality = {
            "test": "Shapiro-Wilk",
            "w_statistic": float(w_stat),
            "p_value": float(p_val),
            "reject_normality_alpha_0_05": bool(p_val < 0.05),
        }

    one_sample_t: Optional[Dict[str, Any]] = None
    if hypothesized_mean is not None:
        t_stat, p_val = stats.ttest_1samp(arr_x, popmean=hypothesized_mean)
        one_sample_t = {
            "hypothesized_mean": float(hypothesized_mean),
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
            "significant_alpha_0_05": bool(p_val < 0.05),
        }

    regression: Optional[Dict[str, Any]] = None
    if y_values is not None:
        if len(y_values) != len(x_values):
            raise ValueError("y_values must have the exact same length as x_values.")
        arr_y = np.asarray(y_values, dtype=float)
        if not np.all(np.isfinite(arr_y)):
            raise ValueError("y_values must contain only finite real numbers.")
        if float(np.ptp(arr_x)) == 0.0:
            raise ValueError("Cannot run linear regression when all x_values are identical.")
        lin = stats.linregress(arr_x, arr_y)
        y_pred = lin.slope * arr_x + lin.intercept
        residuals = arr_y - y_pred
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        regression = {
            "slope": float(lin.slope),
            "intercept": float(lin.intercept),
            "r_value": float(lin.rvalue),
            "r_squared": float(lin.rvalue ** 2),
            "p_value": float(lin.pvalue),
            "std_err": float(lin.stderr),
            "rmse": rmse,
            "scatter_points": [
                {"x": float(xv), "y": float(yv), "y_pred": float(yp)}
                for xv, yv, yp in zip(arr_x, arr_y, y_pred)
            ],
            "causation_warning": "Statistical correlation (R^2, p-value) does NOT establish causation without controlled experimental design.",
        }

    return {
        "descriptive": descriptive,
        "normality_test": normality,
        "one_sample_t_test": one_sample_t,
        "linear_regression": regression,
    }


def run_monte_carlo_pi(samples: int = 10000, seed: int = 42) -> Dict[str, Any]:
    if not (100 <= samples <= 500000):
        raise ValueError("samples must be between 100 and 500,000.")
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.0, 1.0, size=samples)
    y = rng.uniform(0.0, 1.0, size=samples)
    inside = (x * x + y * y) <= 1.0
    estimate = float(4.0 * np.mean(inside))
    abs_error = float(abs(estimate - np.pi))
    std_error = float(4.0 * np.sqrt(np.mean(inside) * (1.0 - np.mean(inside)) / samples))
    return {
        "samples": samples,
        "seed": seed,
        "pi_estimate": estimate,
        "reference_pi": float(np.pi),
        "absolute_error": abs_error,
        "standard_error": std_error,
    }
