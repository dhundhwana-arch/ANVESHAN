import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import create_app


class TestAPIEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmpdir.name) / "e2e.db")
        self.app = create_app(db_path=self.db_path)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_frontend_served_with_brand_footer_and_security_headers(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Developer by Divyesh Bambhaniya", r.text)
        self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")

    def test_full_vertical_research_workflow(self):
        # 1. System status
        st = self.client.get("/api/system/status")
        self.assertEqual(st.status_code, 200)
        self.assertEqual(st.json()["platform"], "ANVESHAN")

        # 2. Symbolic math
        m = self.client.post("/api/math/symbolic", json={"expression": "x^2 + 3*x", "operation": "differentiate"})
        self.assertEqual(m.status_code, 200)
        self.assertEqual(m.json()["result"]["result"], "2*x + 3")

        # 3. Physics oscillator
        p = self.client.post("/api/physics/oscillator", json={"mass_kg": 1.0, "damping_ns_per_m": 0.4, "stiffness_n_per_m": 4.0})
        self.assertEqual(p.status_code, 200)
        exp_id = p.json()["experiment"]["id"]
        self.assertTrue(p.json()["result"]["numerical_verification"]["stable"])

        # 4. Rerun & verify reproducibility
        rr = self.client.post(f"/api/experiments/{exp_id}/rerun")
        self.assertEqual(rr.status_code, 200)
        self.assertTrue(rr.json()["reproducible"])

        # 5. Create and verify hypothesis
        h = self.client.post(
            "/api/hypotheses",
            json={
                "title": "Decay Half-Life Check",
                "statement": "Radioactive decay solver error remains under 1e-4",
                "assumptions": ["Constant decay rate"],
                "falsifiable_prediction": "max_abs_error_vs_analytical <= 1e-4",
                "test_domain": "physics_decay",
                "test_config": {"n0": 500.0, "half_life_s": 5.0, "duration_s": 25.0},
                "acceptance_criteria": {"metric": "numerical_verification.max_abs_error_vs_analytical", "operator": "<=", "target": 1e-4},
            },
        )
        self.assertEqual(h.status_code, 200)
        hid = h.json()["id"]
        v = self.client.post(f"/api/hypotheses/{hid}/verify", json={})
        self.assertEqual(v.status_code, 200)
        self.assertTrue(v.json()["verification"]["passed"])

        # 6. Validation & security rejection
        bad = self.client.post("/api/math/symbolic", json={"expression": "__import__('os').system('id')", "operation": "simplify"})
        self.assertEqual(bad.status_code, 400)
        bad_phys = self.client.post("/api/physics/oscillator", json={"mass_kg": -5})
        self.assertEqual(bad_phys.status_code, 422)

    def test_v1_2_dataset_cooling_and_export_endpoints(self):
        ds = self.client.post(
            "/api/datasets/analyze",
            json={"filename": "lab.csv", "csv_text": "t,y\n1,3\n2,5\n3,7\n4,9\n", "x_col": "t", "y_col": "y"},
        )
        self.assertEqual(ds.status_code, 200)
        self.assertAlmostEqual(ds.json()["result"]["linear_regression"]["slope"], 2.0, places=6)
        exp_id = ds.json()["experiment"]["id"]

        cool = self.client.post("/api/physics/cooling", json={"t0_c": 85.0, "t_env_c": 25.0, "cooling_k_per_s": 0.04})
        self.assertEqual(cool.status_code, 200)
        self.assertTrue(cool.json()["result"]["numerical_verification"]["stable"])

        log = self.client.post("/api/physics/logistic", json={"p0": 20.0, "carrying_capacity_k": 400.0, "growth_rate_r": 0.2})
        self.assertEqual(log.status_code, 200)
        self.assertTrue(log.json()["result"]["numerical_verification"]["stable"])

        rep = self.client.get(f"/api/experiments/{exp_id}/report")
        self.assertEqual(rep.status_code, 200)
        self.assertIn("ANVESHAN Experiment Evidence Report", rep.text)

        bib = self.client.get("/api/literature/export/bibtex")
        self.assertEqual(bib.status_code, 200)

    def test_version_consistency_1_2_0(self):
        import backend
        from backend.config import get_runtime_versions
        self.assertEqual(backend.__version__, "1.2.0")
        self.assertEqual(get_runtime_versions()["anveshan"], "1.2.0")
        self.assertEqual(self.app.version, "1.2.0")
