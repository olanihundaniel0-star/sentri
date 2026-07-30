"""Transaction domain types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from sentri.canonical.sanitize import sanitize_memo

_RECIPIENT_ID_RE = re.compile(r"^[A-Za-z0-9_\-:.]{1,128}$")
_TIMESTAMP_MAX_PAST_YEARS = 10
_TIMESTAMP_MAX_FUTURE = timedelta(hours=1)


@dataclass(frozen=True)
class Transaction:
    """Internal canonical transaction record."""

    amount_kobo: int
    timestamp: datetime
    recipient_id: str
    currency: str = "NGN"
    memo: Optional[str] = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        object.__setattr__(self, "memo", sanitize_memo(self.memo))


class TransactionEvent(BaseModel):
    """Inbound API payload for a transaction evaluation request."""

    amount_kobo: int = Field(gt=0)
    timestamp: str | int
    recipient_id: str
    currency: str = "NGN"
    device_id: Optional[str] = None
    memo: Optional[str] = None
    user_id: str
    cross_border: bool = False
    language: Optional[str] = None

    @field_validator("memo")
    @classmethod
    def _sanitize_memo(cls, value: Optional[str]) -> Optional[str]:
        return sanitize_memo(value)

    @field_validator("recipient_id")
    @classmethod
    def _validate_recipient_id(cls, value: str) -> str:
        stripped = value.strip()
        if not _RECIPIENT_ID_RE.match(stripped):
            raise ValueError(
                "recipient_id must be 1-128 characters of letters, digits, "
                "underscore, hyphen, colon, or dot"
            )
        return stripped

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, value: str | int) -> str | int:
        """Sanity-check the raw input only. Timezone conversion stays in
        canonical.timestamps.ingest_timestamp, the single ingestion path."""
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(f"timestamp is not a valid ISO 8601 string: {value!r}") from exc
            return value

        if value <= 0:
            raise ValueError(f"timestamp must be a positive Unix timestamp, got {value!r}")

        now = datetime.now(timezone.utc)
        earliest = now - timedelta(days=365 * _TIMESTAMP_MAX_PAST_YEARS)
        latest = now + _TIMESTAMP_MAX_FUTURE
        candidate = datetime.fromtimestamp(value, tz=timezone.utc)
        if not (earliest <= candidate <= latest):
            raise ValueError(
                f"timestamp {value!r} ({candidate.isoformat()}) is outside the "
                f"plausible range {earliest.isoformat()} to {latest.isoformat()}"
            )
        return value
