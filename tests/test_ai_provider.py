import os
import unittest
from unittest.mock import patch

from backend.config import get_settings
from backend.engines.ai_provider import get_ai_provider


class TestAIProviderHonesty(unittest.TestCase):
    def test_missing_api_key_reports_not_configured(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            provider = get_ai_provider(get_settings())
            st = provider.status()
            self.assertEqual(st["status"], "NOT_CONFIGURED")
            res = provider.analyze("Explain harmonic oscillators")
            self.assertEqual(res["status"], "NOT_CONFIGURED")
            self.assertIsNone(res["response"])
            self.assertIn("No fake response", res["message"])
