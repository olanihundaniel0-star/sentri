"""Categorical deviation scoring: currency novelty and cross-border flag."""

from __future__ import annotations

from sentri.models.profile import UserProfile
from sentri.models.transaction import TransactionEvent


def score_categorical(profile: UserProfile, event: TransactionEvent) -> tuple[bool, bool]:
    """Score the categorical dimension: (currency_novelty, cross_border)."""
    currency_novelty = event.currency not in profile.currencies_seen
    cross_border = event.cross_border
    return currency_novelty, cross_border
