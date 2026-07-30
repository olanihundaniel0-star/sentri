"""User profile and social graph types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sentri.models.transaction import Transaction


@dataclass(frozen=True)
class RecipientRollup:
    """Aggregated statistics for a single recipient."""

    recipient_id: str
    count: int
    mean_kobo: float
    std_kobo: float
    min_kobo: int
    max_kobo: int
    first_seen: datetime
    last_seen: datetime
    total_volume_kobo: int
    transactions: tuple[Transaction, ...]


@dataclass
class SocialGraph:
    """BMONI social graph snapshot for proximity scoring."""

    user_id: str
    friends: frozenset[str]
    friends_of_friends: dict[str, frozenset[str]]


@dataclass(frozen=True)
class UserProfile:
    """Behavioral profile built from historical transactions."""

    user_id: str
    recipients: dict[str, RecipientRollup]
    global_mean_kobo: float
    global_std_kobo: float
    hour_histogram: tuple[int, ...]
    currencies_seen: frozenset[str]
    social_graph: Optional[SocialGraph] = None


def all_transactions(profile: UserProfile) -> list[Transaction]:
    """Every transaction across all of a profile's recipients."""
    return [tx for rollup in profile.recipients.values() for tx in rollup.transactions]
