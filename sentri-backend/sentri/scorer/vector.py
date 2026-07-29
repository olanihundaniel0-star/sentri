"""Assembles the deterministic Tier 1 deviation vector and threshold rules."""

from __future__ import annotations

from datetime import datetime

from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.models.profile import UserProfile
from sentri.models.transaction import TransactionEvent
from sentri.scorer.amount import score_amount
from sentri.scorer.categorical import score_categorical
from sentri.scorer.recipient import score_recipient
from sentri.scorer.temporal import score_hour

_DRIFT_ANOMALY_THRESHOLD = 2.0


def build_vector(profile: UserProfile, event: TransactionEvent, now: datetime) -> DeviationVector:
    """Run all four scorer dimensions and assemble a DeviationVector."""
    recipient_familiarity, graph_proximity = score_recipient(profile, event, now)
    amount = score_amount(profile, event)
    hour_deviation = score_hour(profile, event)
    currency_novelty, cross_border = score_categorical(profile, event)

    return DeviationVector(
        recipient_familiarity=recipient_familiarity,
        graph_proximity=graph_proximity,
        amount_z_recipient=amount["amount_z_recipient"],
        amount_z_global=amount["amount_z_global"],
        amount_drift_ratio=amount["amount_drift_ratio"],
        hour_deviation=hour_deviation,
        currency_novelty=currency_novelty,
        cross_border=cross_border,
        z_score_path=amount["z_score_path"],
    )


def fires(v: DeviationVector, thresholds: dict[str, float | bool]) -> list[TriggerReason]:
    """Return the list of TriggerReasons whose threshold the vector crosses."""
    reasons: list[TriggerReason] = []

    if v.recipient_familiarity < thresholds["recipient_familiarity_below"]:
        reasons.append(TriggerReason.RECIPIENT_FAMILIARITY)

    if v.graph_proximity is not None and v.graph_proximity < thresholds["graph_proximity_below"]:
        reasons.append(TriggerReason.GRAPH_PROXIMITY)

    if v.amount_z_recipient is not None:
        if abs(v.amount_z_recipient) > thresholds["amount_z_above"]:
            reasons.append(TriggerReason.AMOUNT_Z_RECIPIENT)
    elif abs(v.amount_z_global) > thresholds["amount_z_above"]:
        reasons.append(TriggerReason.AMOUNT_Z_GLOBAL)

    if v.amount_drift_ratio is not None and v.amount_drift_ratio > _DRIFT_ANOMALY_THRESHOLD:
        reasons.append(TriggerReason.AMOUNT_DRIFT)

    if v.hour_deviation > thresholds["hour_deviation_above"]:
        reasons.append(TriggerReason.HOUR_DEVIATION)

    if v.currency_novelty and thresholds.get("currency_novelty", True):
        reasons.append(TriggerReason.CURRENCY_NOVELTY)

    if v.cross_border and thresholds.get("cross_border", True):
        reasons.append(TriggerReason.CROSS_BORDER)

    return reasons


_STRUCTURAL_REASONS = frozenset(
    {TriggerReason.RECIPIENT_FAMILIARITY, TriggerReason.GRAPH_PROXIMITY}
)


def should_intervene(triggered: list[TriggerReason]) -> bool:
    """Decide INTERVENE vs SILENT_PASS from the raw reasons `fires()` returned.

    RECIPIENT_FAMILIARITY and GRAPH_PROXIMITY are structural: they fire for any
    first-time, socially-unconnected recipient regardless of whether anything
    else about the transaction is unusual, so they cannot justify escalation on
    their own. Intervene only when at least one non-structural reason fired,
    whether alone or alongside the structural ones.
    """
    return any(reason not in _STRUCTURAL_REASONS for reason in triggered)
