"""Recipient-dimension deviation scoring: familiarity and graph proximity."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sentri.graph.familiarity import familiarity
from sentri.graph.proximity import proximity
from sentri.models.profile import UserProfile
from sentri.models.transaction import TransactionEvent


def score_recipient(
    profile: UserProfile,
    event: TransactionEvent,
    now: datetime,
) -> tuple[float, Optional[float]]:
    """Score the recipient dimension: (recipient_familiarity, graph_proximity)."""
    recipient_familiarity = familiarity(profile, event.recipient_id, event.amount_kobo, now)
    graph_proximity = proximity(profile.social_graph, event.recipient_id)
    return recipient_familiarity, graph_proximity
