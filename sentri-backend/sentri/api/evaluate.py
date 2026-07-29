"""POST /evaluate: the Tier 1 + Tier 2 transaction evaluation pipeline."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Any

import numpy as np
from fastapi import APIRouter, Depends

from sentri.api.deps import get_bmoni_client, get_synthesizer
from sentri.bmoni.protocol import BMONIClient
from sentri.canonical.timestamps import ingest_timestamp, to_wat
from sentri.config import DEFAULT_LANGUAGE, THRESHOLDS
from sentri.graph.builder import build_profile
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.models.profile import UserProfile
from sentri.models.transaction import Transaction, TransactionEvent
from sentri.models.verdict import Verdict, VerdictKind
from sentri.scorer.vector import build_vector, fires, should_intervene
from sentri.synthesizer.protocol import ExplanationSynthesizer

router = APIRouter()
logger = logging.getLogger(__name__)

_DRIFT_RECENT_WINDOW_DAYS = 30
_DRIFT_PRIOR_WINDOW_END_DAYS = 90
_DRIFT_MIN_WINDOW_SAMPLES = 3


def _exclude_current_event(
    history: list[Transaction], event: TransactionEvent, event_time: datetime
) -> list[Transaction]:
    """Drop the event under evaluation from its own history, if BMONI already recorded it.

    The event being scored hasn't happened from the profile's point of view yet;
    a stub or eagerly-written store may already include it in the returned history.
    """
    return [
        tx
        for tx in history
        if not (
            tx.timestamp == event_time
            and tx.recipient_id == event.recipient_id
            and tx.amount_kobo == event.amount_kobo
        )
    ]


def _format_hour_12h(hour: int) -> str:
    period = "am" if hour < 12 else "pm"
    display_hour = hour % 12 or 12
    return f"{display_hour}{period}"


def _typical_hours(histogram: tuple[int, ...]) -> str:
    if sum(histogram) == 0:
        return "no particular time"
    ranked = sorted(range(24), key=lambda h: histogram[h], reverse=True)
    top_two = sorted(ranked[:2])
    return " and ".join(_format_hour_12h(h) for h in top_two)


def _format_time_of_day(dt: datetime) -> str:
    period = "am" if dt.hour < 12 else "pm"
    display_hour = dt.hour % 12 or 12
    return f"{display_hour}:{dt.minute:02d}{period}"


def format_naira_display(kobo: int) -> str:
    """Format integer kobo as a naira display string without rounding."""
    sign = "-" if kobo < 0 else ""
    absolute_kobo = abs(kobo)
    naira, remainder_kobo = divmod(absolute_kobo, 100)
    display = f"{sign}₦{naira:,}"
    if remainder_kobo:
        display = f"{display}.{remainder_kobo:02d}"
    return display


def _derive_event_id(event: TransactionEvent) -> str:
    """Deterministic ID from the fields that identify the transaction attempt.

    timestamp is normalized via canonical.timestamps.ingest_timestamp before hashing
    so that ISO-string and Unix-int inputs produce the same ID for the same event.
    """
    ts = ingest_timestamp(event.timestamp).isoformat()
    payload = f"{event.user_id}|{ts}|{event.amount_kobo}|{event.recipient_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _add_kobo_fact(facts: dict[str, Any], base_name: str, kobo: int) -> None:
    facts[f"{base_name}_kobo"] = kobo
    facts[f"{base_name}_display"] = format_naira_display(kobo)


def _all_transactions(profile: UserProfile) -> list[Transaction]:
    return [tx for rollup in profile.recipients.values() for tx in rollup.transactions]


def _drift_windows(profile: UserProfile, event: TransactionEvent) -> tuple[list[int], list[int]]:
    reference = ingest_timestamp(event.timestamp)
    recent: list[int] = []
    prior: list[int] = []

    for tx in _all_transactions(profile):
        age_days = (reference - tx.timestamp).total_seconds() / 86400.0
        if 0 <= age_days <= _DRIFT_RECENT_WINDOW_DAYS:
            recent.append(tx.amount_kobo)
        elif _DRIFT_RECENT_WINDOW_DAYS < age_days <= _DRIFT_PRIOR_WINDOW_END_DAYS:
            prior.append(tx.amount_kobo)

    return recent, prior


def _build_facts(
    vector: DeviationVector,
    profile: UserProfile,
    event: TransactionEvent,
    event_time_wat: datetime,
    triggered: list[TriggerReason],
) -> dict[str, Any]:
    """Facts the synthesizer may restate verbatim — every value traceable to profile/event data."""
    facts: dict[str, Any] = {
        "currency": event.currency,
    }
    _add_kobo_fact(facts, "amount", event.amount_kobo)

    rollup = profile.recipients.get(event.recipient_id)
    if vector.amount_z_recipient is not None and rollup is not None:
        _add_kobo_fact(facts, "min_amount", rollup.min_kobo)
        _add_kobo_fact(facts, "max_amount", rollup.max_kobo)
    else:
        all_amounts = [
            tx.amount_kobo for other in profile.recipients.values() for tx in other.transactions
        ]
        if all_amounts:
            _add_kobo_fact(facts, "min_amount", min(all_amounts))
            _add_kobo_fact(facts, "max_amount", max(all_amounts))

    # Drift facts are only useful when AMOUNT_DRIFT fired; new-recipient and
    # under-sampled cases deliberately carry no drift keys.
    if TriggerReason.AMOUNT_DRIFT in triggered and vector.amount_drift_ratio is not None:
        recent, prior = _drift_windows(profile, event)
        if len(recent) >= _DRIFT_MIN_WINDOW_SAMPLES and len(prior) >= _DRIFT_MIN_WINDOW_SAMPLES:
            prior_mean_kobo = round(sum(prior) / len(prior))
            recent_mean_kobo = round(sum(recent) / len(recent))
            _add_kobo_fact(facts, "prior_mean", prior_mean_kobo)
            _add_kobo_fact(facts, "recent_mean", recent_mean_kobo)
            _add_kobo_fact(facts, "prior_std", int(float(np.std(prior))))
            _add_kobo_fact(facts, "recent_std", int(float(np.std(recent))))
            facts["drift_ratio"] = vector.amount_drift_ratio

    facts["time_of_day"] = _format_time_of_day(event_time_wat)
    facts["typical_hours"] = _typical_hours(profile.hour_histogram)

    return facts


@router.post("/evaluate", response_model=Verdict)
async def evaluate(
    event: TransactionEvent,
    bmoni_client: BMONIClient = Depends(get_bmoni_client),
    synthesizer: ExplanationSynthesizer = Depends(get_synthesizer),
) -> Verdict:
    logger.info(
        "evaluate_start",
        extra={"user_id": event.user_id, "recipient_id": event.recipient_id},
    )
    start = time.perf_counter()

    try:
        history = await bmoni_client.get_transaction_history(event.user_id)

        if not history:
            logger.info(
                "evaluate_no_history",
                extra={"user_id": event.user_id, "recipient_id": event.recipient_id},
            )
            return Verdict(kind=VerdictKind.SILENT_PASS, synthesizer_used="none")

        social_graph = await bmoni_client.get_social_graph(event.user_id)

        event_time = ingest_timestamp(event.timestamp)
        history = _exclude_current_event(history, event, event_time)

        profile = build_profile(event.user_id, history, social_graph)

        now = to_wat(datetime.now(timezone.utc))

        vector = build_vector(profile, event, now)
        triggered = fires(vector, THRESHOLDS)

        if not should_intervene(triggered):
            verdict = Verdict(kind=VerdictKind.SILENT_PASS, synthesizer_used="none")
        else:
            facts = _build_facts(vector, profile, event, event_time, triggered)
            explanation, synthesizer_used = await synthesizer.synthesize(
                vector, facts, triggered, event.language or DEFAULT_LANGUAGE
            )
            verdict = Verdict(
                kind=VerdictKind.INTERVENE,
                explanation=explanation,
                triggered_reasons=triggered,
                synthesizer_used=synthesizer_used,
            )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "evaluate_complete",
            extra={
                "user_id": event.user_id,
                "event_id": _derive_event_id(event),
                "verdict_kind": verdict.kind.value,
                "triggered_reasons": (
                    [r.value for r in verdict.triggered_reasons]
                    if verdict.triggered_reasons
                    else []
                ),
                "synthesizer_used": verdict.synthesizer_used,
                "explanation": verdict.explanation,
                "latency_ms": elapsed_ms,
            },
        )
    except (asyncio.CancelledError, KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        logger.error(
            "evaluate_failed",
            exc_info=True,
            extra={"user_id": event.user_id, "recipient_id": event.recipient_id},
        )
        return Verdict(kind=VerdictKind.SILENT_PASS, synthesizer_used="none")

    return verdict
