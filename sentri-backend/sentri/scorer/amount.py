"""Amount-dimension deviation scoring: z-scores and volatility drift."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import Z_SCORE_MIN_SAMPLES
from sentri.models.profile import UserProfile
from sentri.models.transaction import Transaction, TransactionEvent

_RECENT_WINDOW_DAYS = 30
_PRIOR_WINDOW_END_DAYS = 90
_MIN_WINDOW_SAMPLES = 3
_ZERO_VARIANCE_EPSILON = 1e-9


def _all_transactions(profile: UserProfile) -> list[Transaction]:
    return [tx for rollup in profile.recipients.values() for tx in rollup.transactions]


def _amount_drift_ratio(profile: UserProfile, event: TransactionEvent) -> Optional[float]:
    """Ratio of recent (0-30d) to prior (31-90d) amount volatility, relative to the event's own time."""
    reference = ingest_timestamp(event.timestamp)

    recent: list[int] = []
    prior: list[int] = []
    for tx in _all_transactions(profile):
        age_days = (reference - tx.timestamp).total_seconds() / 86400.0
        if 0 <= age_days <= _RECENT_WINDOW_DAYS:
            recent.append(tx.amount_kobo)
        elif _RECENT_WINDOW_DAYS < age_days <= _PRIOR_WINDOW_END_DAYS:
            prior.append(tx.amount_kobo)

    if len(recent) < _MIN_WINDOW_SAMPLES or len(prior) < _MIN_WINDOW_SAMPLES:
        return None

    sigma_recent = float(np.std(recent))
    sigma_prior = float(np.std(prior))
    return sigma_recent / max(sigma_prior, 1.0)


def score_amount(profile: UserProfile, event: TransactionEvent) -> dict[str, Any]:
    """Score the amount dimension: recipient/global z-scores and drift ratio."""
    global_z = (event.amount_kobo - profile.global_mean_kobo) / max(profile.global_std_kobo, 1.0)

    rollup = profile.recipients.get(event.recipient_id)
    if rollup is None or rollup.count < Z_SCORE_MIN_SAMPLES:
        recipient_z: Optional[float] = None
        path = "global_z_min_samples"
    elif abs(rollup.std_kobo) < _ZERO_VARIANCE_EPSILON:
        recipient_z = None
        path = "global_z_zero_variance"
    else:
        recipient_z = (event.amount_kobo - rollup.mean_kobo) / rollup.std_kobo
        path = "recipient_z"

    return {
        "amount_z_recipient": recipient_z,
        "amount_z_global": global_z,
        "amount_drift_ratio": _amount_drift_ratio(profile, event),
        "z_score_path": path,
    }
