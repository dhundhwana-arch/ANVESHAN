import math
import unittest

from backend.engines.physics_engine import (
    simulate_damped_harmonic_oscillator,
    simulate_projectile_with_drag,
    simulate_radioactive_decay,
)


class TestPhysicsEngine(unittest.TestCase):
    def test_oscillator_all_three_damping_regimes(self):
        for c, expected_regime in [(0.4, "underdamped"), (4.0, "critically_damped"), (6.0, "overdamped")]:
            res = simulate_damped_harmonic_oscillator(mass_kg=1.0, damping_ns_per_m=c, stiffness_n_per_m=4.0)
            self.assertEqual(res["derived_parameters"]["regime"], expected_regime)
            self.assertTrue(res["numerical_verification"]["stable"])
            self.assertLess(res["numerical_verification"]["max_abs_error_vs_analytical_m"], 1e-5)
            self.assertTrue(res["numerical_verification"]["energy_non_increasing_check"])

    def test_projectile_vacuum_matches_analytical_and_drag_reduces_range(self):
        vac = simulate_projectile_with_drag(v0_m_per_s=30.0, angle_deg=45.0, drag_coeff=0.0)
        self.assertLess(vac["numerical_verification"]["vacuum_limit_error_m"], 1e-4)

        drag = simulate_projectile_with_drag(v0_m_per_s=30.0, angle_deg=45.0, drag_coeff=0.47)
        self.assertLess(drag["results"]["range_m"], drag["results"]["vacuum_analytical_range_m"])
        self.assertTrue(drag["numerical_verification"]["physical_consistency_check"])

    def test_radioactive_decay_half_life_accuracy(self):
        res = simulate_radioactive_decay(n0=1000.0, half_life_s=10.0, duration_s=10.0, num_points=50)
        self.assertTrue(res["numerical_verification"]["stable"])
        self.assertAlmostEqual(res["derived_parameters"]["remaining_at_end"], 500.0, places=3)

    def test_invalid_physics_parameters_rejected(self):
        with self.assertRaises(ValueError):
            simulate_damped_harmonic_oscillator(mass_kg=-1.0)
        with self.assertRaises(ValueError):
            simulate_projectile_with_drag(angle_deg=95.0)
