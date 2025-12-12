from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _dotenv_loaded() -> bool:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
        return True
    except Exception:
        return False


def get(key: str) -> str:
    """Get a secret from env or `.env`.

    Priority:
      1) Environment variables (e.g. GitHub Actions secrets)
      2) `.env` file (local development)

    Raises:
        KeyError: if the secret is missing
    """

    value = os.getenv(key)
    if value:
        return value

    _dotenv_loaded()
    value = os.getenv(key)
    if value:
        return value

    raise KeyError(f"Secret '{key}' not found in env or .env file")
