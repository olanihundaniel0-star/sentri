"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_SEEDS_PATH = Path(__file__).resolve().parent.parent / "seeds" / "data.json"


@pytest.fixture
def seed_data() -> dict[str, Any]:
    """Load seeds/data.json when it exists; otherwise return an empty dict."""
    if not _SEEDS_PATH.is_file():
        return {}
    raw = _SEEDS_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    return json.loads(raw)
