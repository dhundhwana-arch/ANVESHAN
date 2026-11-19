import unittest

from backend.engines.export_engine import export_literature_bibtex, generate_experiment_markdown_report
from backend.engines.physics_engine import simulate_logistic_growth, simulate_thermal_cooling


class TestExportAndExtendedPhysics(unittest.TestCase):
    def test_thermal_cooling_and_logistic_growth_accuracy(self):
        cool = simulate_thermal_cooling(t0_c=90.0, t_env_c=20.0, cooling_k_per_s=0.05, duration_s=100.0)
        self.assertTrue(cool["numerical_verification"]["stable"])
        self.assertLess(cool["numerical_verification"]["max_abs_error_vs_analytical_c"], 1e-5)

        log = simulate_logistic_growth(p0=10.0, carrying_capacity_k=500.0, growth_rate_r=0.3, duration_t=30.0)
        self.assertTrue(log["numerical_verification"]["stable"])
        self.assertLess(log["numerical_verification"]["max_abs_error_vs_analytical"], 1e-4)

    def test_bibtex_and_markdown_report_generation(self):
        empty_bib = export_literature_bibtex([])
        self.assertIn("No saved literature sources", empty_bib)

        bib = export_literature_bibtex(
            [
                {
                    "provider": "arxiv",
                    "external_id": "2401.12345",
                    "title": "Test Paper",
                    "authors": ["A. Researcher"],
                    "published_date": "2024-01-15",
                    "source_url": "https://arxiv.org/abs/2401.12345",
                    "access_scope": "METADATA_AND_ABSTRACT",
                }
            ]
        )
        self.assertIn("@misc{arxiv_2401_12345_2024", bib)
        self.assertIn("https://arxiv.org/abs/2401.12345", bib)

        md = generate_experiment_markdown_report(
            {
                "id": "exp_abc",
                "created_at": "2026-11-19T00:00:00Z",
                "domain": "physics_cooling",
                "epistemic_label": "COMPUTATIONAL_RESULT",
                "status": "COMPLETED",
                "input_checksum": "deadbeef",
                "seed": None,
                "reproduction_command": "POST /api/experiments/exp_abc/rerun",
                "research_question": "Cooling check",
                "methodology": "RK45",
                "parameters": {"t0_c": 90.0},
                "output": {"trajectory": [1, 2, 3]},
                "software_versions": {"python": "3.11.2"},
            }
        )
        self.assertIn("Developer by Divyesh Bambhaniya", md)
        self.assertIn("exp_abc", md)

    def test_bibtex_escapes_all_latex_special_characters(self):
        import re
        bib = export_literature_bibtex(
            [
                {
                    "provider": "openalex",
                    "external_id": "10.1000/a&b%c_d#e$f",
                    "title": "100% Yield & Cost $50 #1_Test {Braces}",
                    "authors": ["A_Author & Co."],
                    "published_date": "2025-02-01",
                    "source_url": "https://doi.org/10.1000/test",
                    "access_scope": "METADATA_AND_ABSTRACT",
                }
            ]
        )
        # Verify title and note lines contain zero unescaped %, &, _, #, $
        for line in bib.splitlines():
            if line.strip().startswith(("title =", "author =", "note =")):
                self.assertIsNone(re.search(r"(?<!\\)[%&_#$]", line), f"Unescaped special char in: {line}")
        self.assertIn(r"100\% Yield \& Cost \$50 \#1\_Test Braces", bib)
