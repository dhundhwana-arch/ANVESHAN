import math
from typing import Any, Dict, List

import numpy as np
from scipy.integrate import solve_ivp


def simulate_damped_harmonic_oscillator(
    mass_kg: float = 1.0,
    damping_ns_per_m: float = 0.4,
    stiffness_n_per_m: float = 4.0,
    x0_m: float = 1.0,
    v0_m_per_s: float = 0.0,
    duration_s: float = 12.0,
    num_points: int = 160,
) -> Dict[str, Any]:
    if mass_kg <= 0 or stiffness_n_per_m <= 0 or damping_ns_per_m < 0:
        raise ValueError("mass_kg > 0, stiffness_n_per_m > 0, and damping_ns_per_m >= 0 are required.")
    if not (0.1 <= duration_s <= 200.0):
        raise ValueError("duration_s must be between 0.1 and 200.0 seconds.")
    if not (20 <= num_points <= 1000):
        raise ValueError("num_points must be between 20 and 1000.")

    def ode(_t: float, state: List[float]) -> List[float]:
        x, v = state
        return [v, -(damping_ns_per_m / mass_kg) * v - (stiffness_n_per_m / mass_kg) * x]

    t_eval = np.linspace(0.0, duration_s, num_points)
    sol = solve_ivp(ode, (0.0, duration_s), [x0_m, v0_m_per_s], t_eval=t_eval, method="RK45", rtol=1e-8, atol=1e-10)
    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")

    omega_0 = math.sqrt(stiffness_n_per_m / mass_kg)
    zeta = damping_ns_per_m / (2.0 * math.sqrt(mass_kg * stiffness_n_per_m))

    # Exact closed-form analytical solution for verification
    if abs(zeta - 1.0) < 1e-9:
        regime = "critically_damped"
        a = x0_m
        b = v0_m_per_s + omega_0 * x0_m
        x_exact = (a + b * t_eval) * np.exp(-omega_0 * t_eval)
    elif zeta < 1.0:
        regime = "underdamped"
        omega_d = omega_0 * math.sqrt(1.0 - zeta ** 2)
        a = x0_m
        b = (v0_m_per_s + zeta * omega_0 * x0_m) / omega_d
        x_exact = np.exp(-zeta * omega_0 * t_eval) * (a * np.cos(omega_d * t_eval) + b * np.sin(omega_d * t_eval))
    else:
        regime = "overdamped"
        root = omega_0 * math.sqrt(zeta ** 2 - 1.0)
        r1 = -zeta * omega_0 + root
        r2 = -zeta * omega_0 - root
        c1 = (v0_m_per_s - r2 * x0_m) / (r1 - r2)
        c2 = x0_m - c1
        x_exact = c1 * np.exp(r1 * t_eval) + c2 * np.exp(r2 * t_eval)

    x_num = sol.y[0]
    v_num = sol.y[1]
    energy = 0.5 * mass_kg * (v_num ** 2) + 0.5 * stiffness_n_per_m * (x_num ** 2)
    abs_err = np.abs(x_num - x_exact)
    max_abs_error = float(np.max(abs_err))
    rmse = float(np.sqrt(np.mean(abs_err ** 2)))
    # Energy should be non-increasing (up to tiny numerical tolerance 1e-6 J)
    energy_monotonic = bool(np.all(np.diff(energy) <= 1e-6))

    trajectory = [
        {
            "t_s": round(float(t), 5),
            "x_numerical_m": round(float(xn), 6),
            "x_analytical_m": round(float(xa), 6),
            "v_m_per_s": round(float(vn), 6),
            "energy_j": round(float(en), 6),
        }
        for t, xn, xa, vn, en in zip(t_eval, x_num, x_exact, v_num, energy)
    ]

    return {
        "model": "damped_harmonic_oscillator",
        "solver": "scipy.integrate.solve_ivp (RK45, rtol=1e-8, atol=1e-10)",
        "units": {"x": "m", "v": "m/s", "t": "s", "energy": "J", "omega_0": "rad/s"},
        "derived_parameters": {
            "natural_frequency_rad_s": omega_0,
            "damping_ratio_zeta": zeta,
            "regime": regime,
            "initial_energy_j": float(energy[0]),
            "final_energy_j": float(energy[-1]),
        },
        "numerical_verification": {
            "max_abs_error_vs_analytical_m": max_abs_error,
            "rmse_vs_analytical_m": rmse,
            "energy_non_increasing_check": energy_monotonic,
            "stable": bool(max_abs_error < 1e-4 and energy_monotonic),
        },
        "trajectory": trajectory,
    }


def simulate_projectile_with_drag(
    v0_m_per_s: float = 40.0,
    angle_deg: float = 45.0,
    mass_kg: float = 0.145,
    drag_coeff: float = 0.47,
    area_m2: float = 0.0042,
    air_density_kg_m3: float = 1.225,
    gravity_m_s2: float = 9.80665,
) -> Dict[str, Any]:
    if v0_m_per_s <= 0 or mass_kg <= 0 or gravity_m_s2 <= 0:
        raise ValueError("v0_m_per_s, mass_kg, and gravity_m_s2 must be positive.")
    if not (1.0 <= angle_deg <= 89.0):
        raise ValueError("angle_deg must be between 1 and 89 degrees.")
    if drag_coeff < 0 or area_m2 < 0 or air_density_kg_m3 < 0:
        raise ValueError("drag_coeff, area_m2, and air_density_kg_m3 must be non-negative.")

    theta = math.radians(angle_deg)
    vx0 = v0_m_per_s * math.cos(theta)
    vy0 = v0_m_per_s * math.sin(theta)
    k_drag = 0.5 * air_density_kg_m3 * drag_coeff * area_m2

    # Analytical vacuum reference
    t_flight_vacuum = 2.0 * vy0 / gravity_m_s2
    range_vacuum = (v0_m_per_s ** 2) * math.sin(2.0 * theta) / gravity_m_s2
    max_height_vacuum = (vy0 ** 2) / (2.0 * gravity_m_s2)

    def ode(_t: float, state: List[float]) -> List[float]:
        _x, _y, vx, vy = state
        speed = math.hypot(vx, vy)
        ax = -(k_drag / mass_kg) * speed * vx
        ay = -gravity_m_s2 - (k_drag / mass_kg) * speed * vy
        return [vx, vy, ax, ay]

    def hit_ground(_t: float, state: List[float]) -> float:
        return state[1]

    hit_ground.terminal = True  # type: ignore[attr-defined]
    hit_ground.direction = -1  # type: ignore[attr-defined]

    t_max = max(t_flight_vacuum * 1.5, 5.0)
    sol = solve_ivp(
        ode,
        (0.0, t_max),
        [0.0, 0.0, vx0, vy0],
        events=hit_ground,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
        max_step=max(t_flight_vacuum / 120.0, 0.01),
    )
    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")

    t_impact = float(sol.t_events[0][0]) if len(sol.t_events[0]) > 0 else float(sol.t[-1])
    range_drag = float(sol.y_events[0][0][0]) if len(sol.y_events[0]) > 0 else float(sol.y[0, -1])
    max_height_drag = float(np.max(sol.y[1]))

    trajectory = [
        {"t_s": round(float(t), 4), "x_m": round(float(x), 4), "y_m": round(max(0.0, float(y)), 4)}
        for t, x, y in zip(sol.t, sol.y[0], sol.y[1])
    ]

    return {
        "model": "projectile_with_quadratic_drag",
        "solver": "scipy.integrate.solve_ivp (RK45, ground-impact event detection)",
        "units": {"x": "m", "y": "m", "t": "s", "v": "m/s"},
        "results": {
            "flight_time_s": t_impact,
            "range_m": range_drag,
            "max_height_m": max_height_drag,
            "vacuum_analytical_range_m": range_vacuum,
            "vacuum_analytical_max_height_m": max_height_vacuum,
            "drag_range_reduction_pct": float(100.0 * (1.0 - range_drag / range_vacuum)) if range_vacuum > 0 else 0.0,
        },
        "numerical_verification": {
            "vacuum_limit_error_m": abs(range_drag - range_vacuum) if k_drag == 0 else None,
            "physical_consistency_check": bool(range_drag <= range_vacuum + 1e-4),
        },
        "trajectory": trajectory,
    }


def simulate_radioactive_decay(
    n0: float = 1000.0,
    half_life_s: float = 10.0,
    duration_s: float = 50.0,
    num_points: int = 100,
) -> Dict[str, Any]:
    if n0 <= 0 or half_life_s <= 0 or duration_s <= 0:
        raise ValueError("n0, half_life_s, and duration_s must be strictly positive.")
    lam = math.log(2.0) / half_life_s
    t_eval = np.linspace(0.0, duration_s, num_points)
    sol = solve_ivp(lambda _t, y: [-lam * y[0]], (0.0, duration_s), [n0], t_eval=t_eval, method="RK45", rtol=1e-9, atol=1e-11)
    n_num = sol.y[0]
    n_exact = n0 * np.exp(-lam * t_eval)
    max_err = float(np.max(np.abs(n_num - n_exact)))
    return {
        "model": "radioactive_decay",
        "derived_parameters": {
            "decay_constant_per_s": lam,
            "mean_lifetime_s": 1.0 / lam,
            "half_life_s": half_life_s,
            "remaining_at_end": float(n_num[-1]),
        },
        "numerical_verification": {
            "max_abs_error_vs_analytical": max_err,
            "non_negative_check": bool(np.all(n_num >= 0.0)),
            "stable": bool(max_err < 1e-4),
        },
        "trajectory": [
            {"t_s": round(float(t), 4), "n_numerical": round(float(nn), 5), "n_analytical": round(float(ne), 5)}
            for t, nn, ne in zip(t_eval, n_num, n_exact)
        ],
    }


def simulate_thermal_cooling(
    t0_c: float = 90.0,
    t_env_c: float = 22.0,
    cooling_k_per_s: float = 0.05,
    duration_s: float = 120.0,
    num_points: int = 120,
) -> Dict[str, Any]:
    if cooling_k_per_s <= 0 or duration_s <= 0:
        raise ValueError("cooling_k_per_s and duration_s must be strictly positive.")
    t_eval = np.linspace(0.0, duration_s, num_points)
    sol = solve_ivp(
        lambda _t, y: [-cooling_k_per_s * (y[0] - t_env_c)],
        (0.0, duration_s),
        [t0_c],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-9,
        atol=1e-11,
    )
    t_num = sol.y[0]
    t_exact = t_env_c + (t0_c - t_env_c) * np.exp(-cooling_k_per_s * t_eval)
    max_err = float(np.max(np.abs(t_num - t_exact)))
    # Monotonic convergence toward ambient temperature
    monotonic = bool(
        np.all(np.diff(t_num) <= 1e-6) if t0_c >= t_env_c else np.all(np.diff(t_num) >= -1e-6)
    )
    return {
        "model": "newtons_law_of_cooling",
        "units": {"T": "degC", "t": "s", "k": "1/s"},
        "derived_parameters": {
            "time_constant_tau_s": 1.0 / cooling_k_per_s,
            "final_temp_c": float(t_num[-1]),
            "ambient_temp_c": t_env_c,
        },
        "numerical_verification": {
            "max_abs_error_vs_analytical_c": max_err,
            "monotonic_convergence_check": monotonic,
            "stable": bool(max_err < 1e-4 and monotonic),
        },
        "trajectory": [
            {"t_s": round(float(t), 4), "temp_numerical_c": round(float(tn), 5), "temp_analytical_c": round(float(te), 5)}
            for t, tn, te in zip(t_eval, t_num, t_exact)
        ],
    }


def simulate_logistic_growth(
    p0: float = 10.0,
    carrying_capacity_k: float = 1000.0,
    growth_rate_r: float = 0.25,
    duration_t: float = 40.0,
    num_points: int = 120,
) -> Dict[str, Any]:
    if p0 <= 0 or carrying_capacity_k <= 0 or growth_rate_r <= 0 or duration_t <= 0:
        raise ValueError("p0, carrying_capacity_k, growth_rate_r, and duration_t must be positive.")
    t_eval = np.linspace(0.0, duration_t, num_points)
    sol = solve_ivp(
        lambda _t, y: [growth_rate_r * y[0] * (1.0 - y[0] / carrying_capacity_k)],
        (0.0, duration_t),
        [p0],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-9,
        atol=1e-11,
    )
    p_num = sol.y[0]
    p_exact = carrying_capacity_k / (1.0 + ((carrying_capacity_k - p0) / p0) * np.exp(-growth_rate_r * t_eval))
    max_err = float(np.max(np.abs(p_num - p_exact)))
    return {
        "model": "logistic_growth",
        "derived_parameters": {
            "carrying_capacity_k": carrying_capacity_k,
            "inflection_population": carrying_capacity_k / 2.0,
            "final_population": float(p_num[-1]),
        },
        "numerical_verification": {
            "max_abs_error_vs_analytical": max_err,
            "bounded_non_negative": bool(np.all(p_num >= 0.0)),
            "stable": bool(max_err < 1e-3),
        },
        "trajectory": [
            {"t": round(float(t), 4), "p_numerical": round(float(pn), 5), "p_analytical": round(float(pe), 5)}
            for t, pn, pe in zip(t_eval, p_num, p_exact)
        ],
    }
