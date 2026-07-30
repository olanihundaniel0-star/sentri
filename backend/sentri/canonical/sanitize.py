"""Ingestion-time sanitization for user-controllable free-text fields."""

from __future__ import annotations

import re
from typing import Optional

_DIRECTIVE_PATTERNS = re.compile(
    r"(ignore\s+previous\s+instructions|disregard\s+the\s+above|"
    r"new\s+instructions?|system\s+prompt|you\s+are\s+now|"
    r"forget\s+everything|override\s+.*\s+rules?)",
    re.IGNORECASE,
)
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_MAX_MEMO_LENGTH = 200


def sanitize_memo(memo: Optional[str]) -> Optional[str]:
    """Sanitize user-controllable memo strings per PRD §7d.

    Strips control characters, caps length, and replaces known
    directive-language patterns with [FILTERED]. Defense-in-depth:
    memo does not currently enter the LLM system prompt, but
    sanitizing at ingestion protects against future feature additions
    and log/response leakage.
    """
    if memo is None:
        return None
    cleaned = _CONTROL_CHARS.sub(" ", memo)
    cleaned = cleaned[:_MAX_MEMO_LENGTH]
    cleaned = _DIRECTIVE_PATTERNS.sub("[FILTERED]", cleaned)
    cleaned = cleaned.strip()
    return cleaned or None
