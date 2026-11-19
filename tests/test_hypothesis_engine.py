import tempfile
import unittest
from pathlib import Path

from backend.database import Database
from backend.engines.hypothesis_engine import rerun_experiment, verify_hypothesis


class TestHypothesisAndReproducibility(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db = Database(str(Path(self.tmpdir.name) / "hyp.db"))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_hypothesis_supported_and_falsified_paths(self):
        # Passing hypothesis
        h_pass = self.db.create_hypothesis(
            title="Oscillator Error Bound",
            statement="RK45 error stays under 1e-4 m",
            assumptions=["Linear damping"],
            falsifiable_prediction="max_abs_error_vs_analytical_m <= 1e-4",
            test_domain="physics_oscillator",
            test_config={"mass_kg": 1.0, "damping_ns_per_m": 0.4, "stiffness_n_per_m": 4.0},
            acceptance_criteria={"metric": "numerical_verification.max_abs_error_vs_analytical_m", "operator": "<=", "target": 1e-4},
        )
        res_pass = verify_hypothesis(self.db, h_pass["id"])
        self.assertTrue(res_pass["verification"]["passed"])
        self.assertEqual(res_pass["verification"]["epistemic_status"], "SUPPORTED_BY_COMPUTATION")

        # Deliberately falsified hypothesis (impossible range > 500m for v0=30 m/s)
        h_fail = self.db.create_hypothesis(
            title="False Range Claim",
            statement="Projectile launched at 30 m/s exceeds 500m range",
            assumptions=["Standard Earth gravity"],
            falsifiable_prediction="range_m > 500",
            test_domain="physics_projectile",
            test_config={"v0_m_per_s": 30.0, "angle_deg": 45.0, "drag_coeff": 0.47},
            acceptance_criteria={"metric": "results.range_m", "operator": ">", "target": 500.0},
        )
        res_fail = verify_hypothesis(self.db, h_fail["id"])
        self.assertFalse(res_fail["verification"]["passed"])
        self.assertEqual(res_fail["verification"]["epistemic_status"], "FALSIFIED_BY_COMPUTATION")
        self.assertEqual(res_fail["experiment"]["epistemic_label"], "FAILED_EXPERIMENT")

    def test_deterministic_rerun_reproducibility(self):
        h = self.db.create_hypothesis(
            title="Seeded Monte Carlo Pi",
            statement="Monte Carlo Pi with seed 777 is reproducible",
            assumptions=["PCG64 PRNG"],
            falsifiable_prediction="absolute_error < 0.08",
            test_domain="monte_carlo_pi",
            test_config={"samples": 15000, "seed": 777},
            acceptance_criteria={"metric": "absolute_error", "operator": "<", "target": 0.08},
        )
        v = verify_hypothesis(self.db, h["id"])
        rerun = rerun_experiment(self.db, v["experiment"]["id"])
        self.assertTrue(rerun["checksum_match"])
        self.assertTrue(rerun["output_checksum_match"])
        self.assertTrue(rerun["reproducible"])
        self.assertEqual(rerun["max_numeric_diff"], 0.0)
