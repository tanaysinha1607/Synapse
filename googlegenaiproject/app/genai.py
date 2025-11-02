"""Gemini 2.0 Flash client factory and helpers using official Google SDK.

Notes:
- Requires `google-genai`.
- We keep a small wrapper to allow easy mocking in tests.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

try:
    # Official SDK import style as of 2025
    from google import genai
except Exception:  # pragma: no cover - allows tests without SDK
    genai = None  # type: ignore

from .config import get_config


class GenAIFactory:
    _client: Optional["genai.Client"] = None

    @classmethod
    def get_client(cls) -> "genai.Client":
        cfg = get_config()
        if cls._client is None:
            if genai is None:
                raise RuntimeError(
                    "google-genai SDK not available. Please install requirements."
                )
            cls._client = genai.Client(api_key=cfg.genai_api_key)
        return cls._client


@retry(wait=wait_exponential(multiplier=0.5, max=8), stop=stop_after_attempt(3))
def generate_text(prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
    """Simple text generation helper for agent prompts.

    Parameters
    ----------
    prompt : str
        The user/content prompt.
    system_instruction : Optional[str]
        System prompt to anchor the model behavior.
    kwargs : Any
        Additional options passed to the SDK.
    """
    cfg = get_config()
    client = GenAIFactory.get_client()
    response = client.models.generate_content(
        model=cfg.genai_model,
        contents=prompt,
        config={"system_instruction": system_instruction, **kwargs},
    )
    # `response.text` is typical; adapt if SDK changes structure
    return getattr(response, "text", str(response))


