import os
import platform
import sqlite3
from pathlib import Path
from typing import Dict

import fastapi
import numpy
import pandas
import pydantic
import scipy
import sympy


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = str(BASE_DIR / "data" / "anveshan.db")


class Settings:
    """Environment-driven configuration. Zero hardcoded secrets."""

    def __init__(self) -> None:
        self.env: str = os.getenv("ANVESHAN_ENV", "development")
        self.db_path: str = os.getenv("ANVESHAN_DB_PATH", DEFAULT_DB_PATH)
        self.ai_provider: str = os.getenv("AI_PROVIDER", "gemini")
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.openalex_email: str = os.getenv("OPENALEX_EMAIL", "").strip()
        self.openalex_api_key: str = os.getenv("OPENALEX_API_KEY", "").strip()


def get_settings() -> Settings:
    return Settings()


def get_runtime_versions() -> Dict[str, str]:
    return {
        "anveshan": "1.2.0",
        "python": platform.python_version(),
        "fastapi": getattr(fastapi, "__version__", "unknown"),
        "pydantic": getattr(pydantic, "__version__", "unknown"),
        "numpy": getattr(numpy, "__version__", "unknown"),
        "scipy": getattr(scipy, "__version__", "unknown"),
        "sympy": getattr(sympy, "__version__", "unknown"),
        "pandas": getattr(pandas, "__version__", "unknown"),
        "sqlite": sqlite3.sqlite_version,
    }
