import math
import unittest

from backend.engines.math_engine import (
    run_monte_carlo_pi,
    run_statistical_analysis,
    run_symbolic_operation,
)


class TestMathEngine(unittest.TestCase):
    def test_symbolic_differentiate_and_integrate(self):
        d = run_symbolic_operation("x^3 + 2*x", operation="differentiate", variable="x", eval_point=2.0)
        self.assertEqual(d["result"], "3*x**2 + 2")
        self.assertAlmostEqual(d["numerical_value"], 14.0, places=9)

        i = run_symbolic_operation("x^2", operation="integrate", variable="x", lower_bound=0.0, upper_bound=3.0)
        self.assertAlmostEqual(i["numerical_value"], 9.0, places=9)

    def test_symbolic_security_injection_blocked(self):
        for payload in [
            "__import__('os').system('ls')",
            "open('/etc/passwd').read()",
            "eval('1+1')",
            "lambda x: x",
        ]:
            with self.assertRaises(ValueError):
                run_symbolic_operation(payload, operation="simplify")

    def test_statistics_and_regression_accuracy(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [3.0, 5.0, 7.0, 9.0, 11.0]  # Exact y = 2x + 1
        res = run_statistical_analysis(x, y, hypothesized_mean=3.0)
        self.assertAlmostEqual(res["descriptive"]["mean"], 3.0, places=9)
        self.assertAlmostEqual(res["linear_regression"]["slope"], 2.0, places=9)
        self.assertAlmostEqual(res["linear_regression"]["intercept"], 1.0, places=9)
        self.assertAlmostEqual(res["linear_regression"]["r_squared"], 1.0, places=9)
        self.assertIn("causation", res["linear_regression"]["causation_warning"].lower())

    def test_monte_carlo_deterministic_seed(self):
        r1 = run_monte_carlo_pi(samples=10000, seed=12345)
        r2 = run_monte_carlo_pi(samples=10000, seed=12345)
        self.assertEqual(r1["pi_estimate"], r2["pi_estimate"])
        self.assertLess(abs(r1["pi_estimate"] - math.pi), 0.1)
