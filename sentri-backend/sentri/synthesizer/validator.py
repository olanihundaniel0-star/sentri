"""Validates LLM-synthesized explanations against the blocklist and source facts."""

from __future__ import annotations

import re
from typing import Any

from sentri.canonical.numeric import canonicalize_money, canonicalize_time, extract_numeric_tokens

_VERDICT_KEYWORDS = [
    "fraud",
    "scam",
    "risky",
    "dangerous",
    "suspicious",
    "warning",
    "alert",
    "beware",
    "cancel",
    "stop",
    "block",
    "avoid",
    "should",
    "shouldn't",
    "don't",
    "do not",
    "careful",
    "be careful",
]

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+")
_MAX_SENTENCES = 3


def _collect_allowed(facts: dict[str, Any]) -> tuple[set[int], set[int], set[int]]:
    money_allowed: set[int] = set()
    time_allowed: set[int] = set()
    integer_allowed: set[int] = set()

    for key, value in facts.items():
        if isinstance(value, bool):
            continue
        if key.endswith("_kobo") and isinstance(value, int):
            money_allowed.add(value)
            continue
        if isinstance(value, str):
            time = canonicalize_time(value)
            if time is not None:
                time_allowed.add(time)
        if isinstance(value, int):
            integer_allowed.add(value)

    return money_allowed, time_allowed, integer_allowed


def _count_sentences(text: str) -> int:
    return len(_SENTENCE_RE.findall(text))


def validate(output: str, facts: dict[str, Any], language: str) -> tuple[bool, str]:
    """Validate a synthesized explanation. Returns (is_valid, failure_reason)."""
    lowered = output.lower()
    for keyword in _VERDICT_KEYWORDS:
        if keyword in lowered:
            return False, "verdict_keyword_present"

    money_allowed, time_allowed, integer_allowed = _collect_allowed(facts)

    for raw, token_type in extract_numeric_tokens(output):
        canonical: Any
        if token_type == "money":
            canonical = canonicalize_money(raw)
            if canonical is None or canonical not in money_allowed:
                return False, f"unsupported_numeric:{raw}"
        elif token_type == "time":
            canonical = canonicalize_time(raw)
            if canonical is None or canonical not in time_allowed:
                return False, f"unsupported_numeric:{raw}"
        else:
            as_int = int(raw)
            money_equiv = canonicalize_money(as_int)
            if as_int not in integer_allowed and (
                money_equiv is None or money_equiv not in money_allowed
            ):
                return False, f"unsupported_numeric:{raw}"

    if _count_sentences(output) > _MAX_SENTENCES:
        return False, "too_long"

    return True, ""
