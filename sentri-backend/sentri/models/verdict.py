"""Verdict types."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from sentri.models.deviation import TriggerReason


class VerdictKind(str, Enum):
    """Final evaluation outcome."""

    SILENT_PASS = "silent_pass"
    INTERVENE = "intervene"


class Verdict(BaseModel):
    """API response for a transaction evaluation."""

    kind: VerdictKind
    explanation: Optional[str] = None
    triggered_reasons: list[TriggerReason] = Field(default_factory=list)
    synthesizer_used: str
