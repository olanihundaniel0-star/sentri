"""Builds a UserProfile from a user's historical transactions."""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

import numpy as np

from sentri.canonical.timestamps import to_wat
from sentri.models.profile import RecipientRollup, SocialGraph, UserProfile
from sentri.models.transaction import Transaction


def _rollup(recipient_id: str, transactions: list[Transaction]) -> RecipientRollup:
    ordered = tuple(sorted(transactions, key=lambda tx: tx.timestamp, reverse=True))
    amounts = [tx.amount_kobo for tx in ordered]
    count = len(ordered)
    std_kobo = 0.0 if count == 1 else float(np.std(amounts))

    return RecipientRollup(
        recipient_id=recipient_id,
        count=count,
        mean_kobo=float(np.mean(amounts)),
        std_kobo=std_kobo,
        min_kobo=min(amounts),
        max_kobo=max(amounts),
        first_seen=min(tx.timestamp for tx in ordered),
        last_seen=max(tx.timestamp for tx in ordered),
        total_volume_kobo=sum(amounts),
        transactions=ordered,
    )


def build_profile(
    user_id: str,
    transactions: list[Transaction],
    social_graph: Optional[SocialGraph],
) -> UserProfile:
    """Aggregate a user's transaction history into a behavioral profile."""
    by_recipient: dict[str, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        by_recipient[tx.recipient_id].append(tx)

    recipients = {
        recipient_id: _rollup(recipient_id, txs) for recipient_id, txs in by_recipient.items()
    }

    all_amounts = [tx.amount_kobo for tx in transactions]
    global_mean_kobo = float(np.mean(all_amounts)) if all_amounts else 0.0
    global_std_kobo = float(np.std(all_amounts)) if all_amounts else 0.0

    hour_counts = [0] * 24
    for tx in transactions:
        hour_counts[to_wat(tx.timestamp).hour] += 1

    currencies_seen = frozenset(tx.currency for tx in transactions)

    return UserProfile(
        user_id=user_id,
        recipients=recipients,
        global_mean_kobo=global_mean_kobo,
        global_std_kobo=global_std_kobo,
        hour_histogram=tuple(hour_counts),
        currencies_seen=currencies_seen,
        social_graph=social_graph,
    )
