"""Application configuration. All values are overridable via environment variables."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

_DEFAULT_THRESHOLDS: dict[str, float | bool] = {
    "recipient_familiarity_below": 0.15,
    "graph_proximity_below": 0.2,
    "amount_z_above": 2.5,
    "hour_deviation_above": 0.7,
    "currency_novelty": True,
    "cross_border": True,
}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return default if raw is None else float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return default if raw is None else int(raw)


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_str_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _env_thresholds(default: dict[str, float | bool]) -> dict[str, float | bool]:
    raw = os.getenv("THRESHOLDS")
    if raw is None:
        return dict(default)
    parsed: dict[str, Any] = json.loads(raw)
    merged = dict(default)
    merged.update(parsed)
    return merged


FAMILIARITY_DECAY_LAMBDA: float = _env_float("FAMILIARITY_DECAY_LAMBDA", 0.01)
FAMILIARITY_VOLUME_FLOOR_RATIO: float = _env_float("FAMILIARITY_VOLUME_FLOOR_RATIO", 0.3)
Z_SCORE_MIN_SAMPLES: int = _env_int("Z_SCORE_MIN_SAMPLES", 3)
THRESHOLDS: dict[str, float | bool] = _env_thresholds(_DEFAULT_THRESHOLDS)
TIMEZONE: str = _env_str("TIMEZONE", "Africa/Lagos")
LLM_MODEL: str = _env_str("LLM_MODEL", "claude-haiku-4-5-20251001")
LLM_MAX_TOKENS: int = _env_int("LLM_MAX_TOKENS", 300)
LLM_TIMEOUT_SECONDS: float = _env_float("LLM_TIMEOUT_SECONDS", 5.0)
SUPPORTED_LANGUAGES: list[str] = _env_str_list("SUPPORTED_LANGUAGES", ["en"])
DEFAULT_LANGUAGE: str = _env_str("DEFAULT_LANGUAGE", "en")
DEBUG_ENDPOINTS_ENABLED: bool = _env_bool("DEBUG_ENDPOINTS_ENABLED", True)
# Sandbox base URL already includes /v1 on every documented path; adapters
# must not append another /v1 prefix. No default for BMONI_API_KEY: it's
# only required once something actually constructs a real BMONIClient
# (sentri.bmoni.client), not at import time, so the rest of the app keeps
# working without it configured.
BMONI_BASE_URL: str = _env_str("BMONI_BASE_URL", "https://embedded-dev.bmoni.com")
BMONI_API_KEY: Optional[str] = os.getenv("BMONI_API_KEY")
