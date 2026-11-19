import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import create_app


class TestLiveDemoWebsite(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.app = create_app(db_path=str(Path(self.tmpdir.name) / "demo_ui.db"))
        self.client = TestClient(self.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_live_demo_navigation_cards_and_brand_identity(self):
        html = self.client.get("/").text
        required_nav = [
            "Overview",
            "Mathematical Lab",
            "Physics Lab",
            "Hypothesis Lab",
            "Data Analysis",
            "Experiment Ledger",
            "Literature Explorer",
            "AI Synthesis",
            "Documentation",
        ]
        for label in required_nav:
            self.assertIn(label, html)
        self.assertIn("Explore Live Demos", html)
        self.assertIn("Try Live Demo", html)
        self.assertIn("Developer by Divyesh Bambhaniya", html)
        self.assertIn("DIVYESH BAMBHANIYA", html)

    def test_frontend_js_wires_all_real_backend_endpoints(self):
        js = self.client.get("/static/app.js").text
        expected_endpoints = [
            "/api/system/status",
            "/api/math/symbolic",
            "/api/math/statistics",
            "/api/math/monte-carlo-pi",
            "/api/physics/oscillator",
            "/api/physics/projectile",
            "/api/physics/decay",
            "/api/physics/cooling",
            "/api/physics/logistic",
            "/api/hypotheses",
            "/api/datasets/analyze",
            "/api/experiments",
            "/api/literature/search",
            "/api/literature/export/bibtex",
            "/api/ai/analyze",
        ]
        for ep in expected_endpoints:
            self.assertIn(ep, js)
