"""Timestamp ingestion and West Africa Time conversion."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Union
from zoneinfo import ZoneInfo

_WAT = ZoneInfo("Africa/Lagos")


def ingest_timestamp(value: Union[str, int]) -> datetime:
    """Parse an API timestamp and normalize it to West Africa Time."""
    if isinstance(value, int):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
        # Nigeria does not observe DST. Hour-of-day is stable. Do not add DST handling here.
        return dt.astimezone(_WAT)

    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError(f"timestamp is naive and must be timezone-aware: {value!r}")
        # Nigeria does not observe DST. Hour-of-day is stable. Do not add DST handling here.
        return dt.astimezone(_WAT)

    raise TypeError(f"unsupported timestamp type: {type(value).__name__}")


def to_wat(dt: datetime) -> datetime:
    """Convert an aware datetime to West Africa Time."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(_WAT)
