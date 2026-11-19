from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx

from backend.config import Settings


class AIProvider(ABC):
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def analyze(self, prompt: str, context: str = "") -> Dict[str, Any]:
        ...


class GeminiProvider(AIProvider):
    """Replaceable Google Gemini REST adapter. Never fabricates responses when unconfigured."""

    ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    def status(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "provider": "gemini",
                "model": self.model,
                "status": "NOT_CONFIGURED",
                "message": "GEMINI_API_KEY is not set. Core math, physics, and hypothesis engines work fully without it. Obtain a key at https://aistudio.google.com/docs/api-key.",
            }
        return {
            "provider": "gemini",
            "model": self.model,
            "status": "CONFIGURED_UNVERIFIED",
            "message": "GEMINI_API_KEY is present in environment variables (never exposed to frontend).",
        }

    def analyze(self, prompt: str, context: str = "") -> Dict[str, Any]:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        if not self.api_key:
            return {
                "status": "NOT_CONFIGURED",
                "provider": "gemini",
                "model": self.model,
                "epistemic_label": "UNVERIFIED_CLAIM",
                "response": None,
                "message": "GEMINI_API_KEY is missing. Configure it in .env to enable live AI synthesis. No fake response was generated.",
            }

        url = self.ENDPOINT_TEMPLATE.format(model=self.model)
        system_prefix = (
            "You are a scientific research assistant in ANVESHAN. "
            "Distinguish established facts from hypotheses, never invent citations, and report uncertainty honestly.\n\n"
        )
        full_text = f"{system_prefix}Context:\n{context}\n\nRequest:\n{prompt}" if context else f"{system_prefix}{prompt}"
        payload = {"contents": [{"parts": [{"text": full_text}]}]}

        try:
            resp = httpx.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "status": "CONNECTED",
                "provider": "gemini",
                "model": self.model,
                "epistemic_label": "PROPOSED_HYPOTHESIS",
                "response": text,
                "message": "Live response generated via Gemini API. Treat AI output as hypothesis until computationally or empirically verified.",
            }
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError, OSError) as exc:
            return {
                "status": "NOT_CONNECTED",
                "provider": "gemini",
                "model": self.model,
                "epistemic_label": "UNVERIFIED_CLAIM",
                "response": None,
                "message": f"Network unavailable while calling Gemini API ({type(exc).__name__}).",
            }
        except httpx.HTTPStatusError as exc:
            return {
                "status": "UPSTREAM_ERROR",
                "provider": "gemini",
                "model": self.model,
                "epistemic_label": "UNVERIFIED_CLAIM",
                "response": None,
                "message": f"Gemini API returned HTTP {exc.response.status_code}.",
            }


def get_ai_provider(settings: Settings) -> AIProvider:
    return GeminiProvider(settings)
