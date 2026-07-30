"""Recipient familiarity scoring."""

from __future__ import annotations

import math
from datetime import datetime

from sentri.config import FAMILIARITY_DECAY_LAMBDA, FAMILIARITY_VOLUME_FLOOR_RATIO
from sentri.models.profile import UserProfile


def familiarity(
    profile: UserProfile,
    recipient_id: str,
    requested_amount_kobo: int,
    now: datetime,
) -> float:
    """Score how familiar a user is with a recipient, in [0, 1].

    Recency-weighted transaction count normalized to [0, 1], with a volume
    floor that caps familiarity for recipients who have only ever received
    trivial amounts (PRD threat model 7(a): recipient conditioning attacks).
    """
    rollup = profile.recipients.get(recipient_id)
    if rollup is None:
        return 0.0

    raw = 0.0
    for tx in rollup.transactions:
        age_days = (now - tx.timestamp).total_seconds() / 86400.0
        raw += math.exp(-FAMILIARITY_DECAY_LAMBDA * age_days)

    score = raw / (raw + 1.0)

    if rollup.total_volume_kobo < FAMILIARITY_VOLUME_FLOOR_RATIO * requested_amount_kobo:
        score = min(score, 0.2)

    return score
