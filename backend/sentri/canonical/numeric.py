"""Numeric canonicalization for money, time, and token extraction."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Literal, Optional, Union

TokenType = Literal["money", "time", "integer"]

_CURRENCY_PREFIX_RE = re.compile(r"^NGN\s*", re.IGNORECASE)
_MONEY_NAIRA_RE = re.compile(r"₦(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
_MONEY_NGN_RE = re.compile(r"NGN\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", re.IGNORECASE)
_TIME_RE = re.compile(r"\d{1,2}:\d{2}(?:am|pm)?", re.IGNORECASE)
_INTEGER_RE = re.compile(r"\d+")


def canonicalize_money(value: Union[str, int, float]) -> Optional[int]:
    """Convert a monetary value to integer kobo."""
    if isinstance(value, (int, float)):
        return int(value * 100)

    if not isinstance(value, str):
        return None

    stripped = value.strip()
    if not stripped:
        return None

    normalized = stripped.replace("₦", "")
    normalized = _CURRENCY_PREFIX_RE.sub("", normalized)
    normalized = normalized.replace(",", "").replace(" ", "")

    if any(char.isalpha() for char in normalized):
        return None

    if not normalized:
        return None

    try:
        amount_naira = Decimal(normalized)
    except InvalidOperation:
        return None

    return int(amount_naira * 100)


def canonicalize_time(value: str) -> Optional[int]:
    """Parse a clock time and return minutes since midnight."""
    text = value.strip()
    if not text:
        return None

    match = re.fullmatch(r"(\d{1,2}):(\d{2})(?::(\d{2}))?(am|pm)?", text, flags=re.IGNORECASE)
    if match is None:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = match.group(4).lower() if match.group(4) else None

    if minute > 59:
        return None

    if meridiem is None:
        if hour == 24 or hour > 23:
            return None
        return hour * 60 + minute

    if hour < 1 or hour > 12:
        return None

    if meridiem == "am":
        hour = 0 if hour == 12 else hour
    else:
        hour = 12 if hour == 12 else hour + 12

    return hour * 60 + minute


def _span_overlaps(start: int, end: int, occupied: list[tuple[int, int]]) -> bool:
    return any(not (end <= occ_start or start >= occ_end) for occ_start, occ_end in occupied)


def extract_numeric_tokens(text: str) -> list[tuple[str, TokenType]]:
    """Extract numeric tokens from free text in order of appearance."""
    candidates: list[tuple[int, int, str, TokenType, int]] = []
    priority = {"money": 0, "time": 1, "integer": 2}

    for pattern in (_MONEY_NAIRA_RE, _MONEY_NGN_RE):
        for match in pattern.finditer(text):
            candidates.append(
                (match.start(), match.end(), match.group(), "money", priority["money"])
            )

    for match in _TIME_RE.finditer(text):
        candidates.append((match.start(), match.end(), match.group(), "time", priority["time"]))

    for match in _INTEGER_RE.finditer(text):
        candidates.append(
            (match.start(), match.end(), match.group(), "integer", priority["integer"])
        )

    candidates.sort(key=lambda item: (item[0], item[4], -(item[1] - item[0])))

    selected: list[tuple[int, int, str, TokenType]] = []
    occupied: list[tuple[int, int]] = []

    for start, end, raw, token_type, _ in candidates:
        if _span_overlaps(start, end, occupied):
            continue
        selected.append((start, end, raw, token_type))
        occupied.append((start, end))

    selected.sort(key=lambda item: item[0])
    return [(raw, token_type) for _, _, raw, token_type in selected]
