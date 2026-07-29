"""Tests for /evaluate helper behavior."""

from __future__ import annotations

from datetime import datetime, timezone
from math import isclose

import numpy as np
from sentri.api.evaluate import _build_facts, format_naira_display
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.models.profile import RecipientRollup, UserProfile
from sentri.models.transaction import Transaction, TransactionEvent


def test_format_naira_display_preserves_kobo_precision() -> None:
    assert format_naira_display(45_000_000) == "₦450,000"
    assert format_naira_display(45_012_375) == "₦450,123.75"


def test_build_facts_emits_kobo_and_display_amounts() -> None:
    timestamp = datetime(2026, 7, 27, 10, 30, tzinfo=timezone.utc)
    transactions = (
        Transaction(
            amount_kobo=10_000,
            timestamp=timestamp.replace(day=26),
            recipient_id="recipient",
        ),
        Transaction(
            amount_kobo=40_000,
            timestamp=timestamp.replace(day=25),
            recipient_id="recipient",
        ),
        Transaction(
            amount_kobo=70_000,
            timestamp=timestamp.replace(day=24),
            recipient_id="recipient",
        ),
        Transaction(
            amount_kobo=12_345,
            timestamp=timestamp.replace(month=6, day=10),
            recipient_id="recipient",
        ),
        Transaction(
            amount_kobo=20_000,
            timestamp=timestamp.replace(month=6, day=5),
            recipient_id="recipient",
        ),
        Transaction(
            amount_kobo=45_012_375,
            timestamp=timestamp.replace(month=5, day=30),
            recipient_id="recipient",
        ),
    )
    amounts = [tx.amount_kobo for tx in transactions]
    profile = UserProfile(
        user_id="user",
        recipients={
            "recipient": RecipientRollup(
                recipient_id="recipient",
                count=len(transactions),
                mean_kobo=22_512_360,
                std_kobo=1,
                min_kobo=min(amounts),
                max_kobo=max(amounts),
                first_seen=min(tx.timestamp for tx in transactions),
                last_seen=max(tx.timestamp for tx in transactions),
                total_volume_kobo=sum(amounts),
                transactions=transactions,
            )
        },
        global_mean_kobo=22_512_360,
        global_std_kobo=1,
        hour_histogram=(0,) * 24,
        currencies_seen=frozenset({"NGN"}),
    )
    vector = DeviationVector(
        recipient_familiarity=1.0,
        graph_proximity=None,
        amount_z_recipient=3.0,
        amount_z_global=0.0,
        amount_drift_ratio=2.0,
        hour_deviation=0.0,
        currency_novelty=False,
        cross_border=False,
        z_score_path="recipient_z",
    )
    event = TransactionEvent(
        amount_kobo=45_012_375,
        timestamp=timestamp.isoformat(),
        recipient_id="recipient",
        user_id="user",
    )

    facts = _build_facts(vector, profile, event, timestamp, [TriggerReason.AMOUNT_DRIFT])
    recent = [10_000, 40_000, 70_000]
    prior = [12_345, 20_000, 45_012_375]

    assert facts["amount_kobo"] == 45_012_375
    assert facts["amount_display"] == "₦450,123.75"
    assert facts["min_amount_kobo"] == 10_000
    assert facts["min_amount_display"] == "₦100"
    assert facts["max_amount_kobo"] == 45_012_375
    assert facts["max_amount_display"] == "₦450,123.75"
    assert facts["prior_mean_kobo"] == round(sum(prior) / len(prior))
    assert facts["prior_mean_display"] == "₦150,149.07"
    assert facts["recent_mean_kobo"] == round(sum(recent) / len(recent))
    assert facts["recent_mean_display"] == "₦400"
    assert facts["prior_std_kobo"] == int(float(np.std(prior)))
    assert facts["recent_std_kobo"] == int(float(np.std(recent)))
    assert isclose(facts["drift_ratio"], 2.0)
    assert "amount" not in facts
