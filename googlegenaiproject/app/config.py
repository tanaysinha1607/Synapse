"""Application configuration and environment handling.

Environment-based configuration that defaults to asia-south2 and Gemini 2.0
Flash for the hackathon. Values can be overridden via environment variables or
an optional .env file during local development.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
# app/config.py
from pathlib import Path

# Project root = one level above the app package
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Canonical outputs directory at project root: <repo>/outputs
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    gcp_project: str
    gcp_region: str
    firestore_emulator_host: Optional[str]
    genai_model: str
    genai_api_key: Optional[str]
    coursera_api_key: Optional[str]
    youtube_api_key: Optional[str]
    rapidapi_key: Optional[str]
    rapidapi_udemy_host: Optional[str]


def get_config() -> AppConfig:
    return AppConfig(
        gcp_project=os.getenv("GCP_PROJECT", "genai-hackathon"),
        gcp_region=os.getenv("GCP_REGION", "asia-south2"),
        firestore_emulator_host=os.getenv("FIRESTORE_EMULATOR_HOST"),
        genai_model=os.getenv("GENAI_MODEL", "models/gemini-2.0-flash"),
        genai_api_key=os.getenv("GENAI_API_KEY"),
        coursera_api_key=os.getenv("COURSERA_API_KEY"),
        youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
        rapidapi_key=os.getenv("RAPIDAPI_KEY"),
        rapidapi_udemy_host=os.getenv("RAPIDAPI_UDEMY_HOST"),
    )


