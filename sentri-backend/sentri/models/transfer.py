"""Request/response types for POST /transfer (Prompt 13)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from sentri.models.deviation import TriggerReason
from sentri.models.verdict import VerdictKind


class TransferRequest(BaseModel):
    """A pending real-money BMONI withdrawal, scored before BMONI ever sees it.

    user_id must be a synthetic seed user bridged to a real BMONI identity
    (see sentri.bmoni.identity_bridge and seeds/identity_bridge.json).
    """

    user_id: str
    amount_kobo: int = Field(gt=0)
    recipient_id: str
    currency: str = "NGN"
    destination_type: Literal["nigeria", "crypto"] = "nigeria"
    destination: dict[str, Any]
    memo: Optional[str] = None
    cross_border: bool = False
    language: Optional[str] = None


class TransferStatus(str, Enum):
    """Outcome of a POST /transfer or /transfer/{id}/confirm call."""

    HELD = "held"
    EXECUTED = "executed"


class TransferResponse(BaseModel):
    """API response for a transfer attempt."""

    status: TransferStatus
    transfer_id: Optional[str] = None
    kind: Optional[VerdictKind] = None
    explanation: Optional[str] = None
    triggered_reasons: list[TriggerReason] = Field(default_factory=list)
    bmoni_result: Optional[dict[str, Any]] = None
