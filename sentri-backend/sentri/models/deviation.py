"""Deviation scoring types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TriggerReason(str, Enum):
    """Reasons a deviation threshold was exceeded."""

    RECIPIENT_FAMILIARITY = "recipient_familiarity"
    GRAPH_PROXIMITY = "graph_proximity"
    AMOUNT_Z_RECIPIENT = "amount_z_recipient"
    AMOUNT_Z_GLOBAL = "amount_z_global"
    AMOUNT_DRIFT = "amount_drift"
    HOUR_DEVIATION = "hour_deviation"
    CURRENCY_NOVELTY = "currency_novelty"
    CROSS_BORDER = "cross_border"


@dataclass(frozen=True)
class DeviationVector:
    """Deterministic Tier 1 deviation signals for a transaction."""

    recipient_familiarity: float
    graph_proximity: Optional[float]
    amount_z_recipient: Optional[float]
    amount_z_global: float
    amount_drift_ratio: Optional[float]
    hour_deviation: float
    currency_novelty: bool
    cross_border: bool
    z_score_path: str
