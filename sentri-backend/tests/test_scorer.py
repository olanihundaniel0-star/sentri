"""Tests for the deterministic Tier 1 scorer: fires()/should_intervene() threshold
logic, the six seed-data cohorts, and dedicated unit tests per scorer submodule.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from sentri import config
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import Z_SCORE_MIN_SAMPLES
from sentri.graph.builder import build_profile
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.models.profile import RecipientRollup, SocialGraph, UserProfile
from sentri.models.transaction import Transaction, TransactionEvent
from sentri.scorer.amount import score_amount
from sentri.scorer.recipient import score_recipient
from sentri.scorer.temporal import score_hour
from sentri.scorer.vector import build_vector, fires, should_intervene
from seeds.generator import generate_seed_data, write_seed_data

_WAT = ZoneInfo("Africa/Lagos")


def _make_vector(*, currency_novelty: bool = False, cross_border: bool = False) -> DeviationVector:
    return DeviationVector(
        recipient_familiarity=1.0,
        graph_proximity=None,
        amount_z_recipient=None,
        amount_z_global=0.0,
        amount_drift_ratio=None,
        hour_deviation=0.0,
        currency_novelty=currency_novelty,
        cross_border=cross_border,
        z_score_path="global_z_min_samples",
    )


def test_currency_novelty_does_not_fire_when_threshold_disabled() -> None:
    vector = _make_vector(currency_novelty=True)
    thresholds = {**config.THRESHOLDS, "currency_novelty": False}

    triggered = fires(vector, thresholds)

    assert TriggerReason.CURRENCY_NOVELTY not in triggered


def test_currency_novelty_fires_with_default_thresholds() -> None:
    vector = _make_vector(currency_novelty=True)

    triggered = fires(vector, config.THRESHOLDS)

    assert TriggerReason.CURRENCY_NOVELTY in triggered


def test_cross_border_does_not_fire_when_threshold_disabled() -> None:
    vector = _make_vector(cross_border=True)
    thresholds = {**config.THRESHOLDS, "cross_border": False}

    triggered = fires(vector, thresholds)

    assert TriggerReason.CROSS_BORDER not in triggered


def test_cross_border_fires_with_default_thresholds() -> None:
    vector = _make_vector(cross_border=True)

    triggered = fires(vector, config.THRESHOLDS)

    assert TriggerReason.CROSS_BORDER in triggered


# ---------------------------------------------------------------------------
# Cohort tests (seed data)
# ---------------------------------------------------------------------------
#
# Each cohort event's own timestamp is fixed relative to the seed generator's
# _REFERENCE_DATE, not to real wall-clock time. `now` here is anchored to that
# same event timestamp (rather than datetime.now()) so these tests stay
# reproducible for as long as the seed data exists — using real "now" would
# make RECIPIENT_FAMILIARITY's exponential recency decay drift further from
# these fixed-calendar transactions every year this suite is run, eventually
# flipping cohorts (e.g. E) that depend on "the recipient is still familiar".


def _exclude_current_event(
    history: list[Transaction], event: TransactionEvent, event_time: datetime
) -> list[Transaction]:
    """Mirror sentri/api/evaluate.py's exclusion: the event under evaluation
    hasn't happened from the profile's point of view yet, but the seed data
    bakes each cohort transaction into that persona's own stored history."""
    return [
        tx
        for tx in history
        if not (
            tx.timestamp == event_time
            and tx.recipient_id == event.recipient_id
            and tx.amount_kobo == event.amount_kobo
        )
    ]


@pytest.fixture(scope="module")
def cohort_cases() -> dict[str, dict[str, Any]]:
    write_seed_data()
    data = generate_seed_data()
    by_cohort: dict[str, dict[str, Any]] = {}
    for test_case in data["test_cases"]:
        by_cohort.setdefault(test_case["cohort"], test_case)
    return by_cohort


async def _cohort_vector_and_triggered(
    test_case: dict[str, Any],
) -> tuple[DeviationVector, list[TriggerReason]]:
    ev = test_case["event"]
    event = TransactionEvent(
        amount_kobo=ev["amount_kobo"],
        timestamp=ev["timestamp"],
        recipient_id=ev["recipient_id"],
        currency=ev["currency"],
        device_id=ev.get("device_id"),
        memo=ev.get("memo"),
        user_id=ev["user_id"],
        cross_border=ev["cross_border"],
    )

    stub = InMemoryBMONIStub()
    history = await stub.get_transaction_history(event.user_id)
    social_graph = await stub.get_social_graph(event.user_id)

    event_time = ingest_timestamp(event.timestamp)
    history = _exclude_current_event(history, event, event_time)

    profile = build_profile(event.user_id, history, social_graph)

    vector = build_vector(profile, event, now=event_time)
    triggered = fires(vector, config.THRESHOLDS)
    return vector, triggered


async def test_cohort_A_pure_amount(cohort_cases: dict[str, dict[str, Any]]) -> None:
    vector, triggered = await _cohort_vector_and_triggered(cohort_cases["A"])

    assert TriggerReason.AMOUNT_Z_GLOBAL in triggered
    assert TriggerReason.RECIPIENT_FAMILIARITY in triggered
    # GRAPH_PROXIMITY is allowed to fire here: the recipient
    # ("..._advance_refund_agent") is not in anyone's friends list, so the
    # graph legitimately places it far — this is the spec's own hedge case,
    # not a violation of "pure amount".
    if TriggerReason.GRAPH_PROXIMITY in triggered:
        assert vector.graph_proximity is not None and vector.graph_proximity < 0.2


async def test_cohort_B_pure_time(cohort_cases: dict[str, dict[str, Any]]) -> None:
    _vector, triggered = await _cohort_vector_and_triggered(cohort_cases["B"])

    assert TriggerReason.HOUR_DEVIATION in triggered
    assert TriggerReason.RECIPIENT_FAMILIARITY in triggered


async def test_cohort_C_synergistic(cohort_cases: dict[str, dict[str, Any]]) -> None:
    _vector, triggered = await _cohort_vector_and_triggered(cohort_cases["C"])

    assert len(triggered) >= 1


async def test_cohort_D_baseline(cohort_cases: dict[str, dict[str, Any]]) -> None:
    _vector, triggered = await _cohort_vector_and_triggered(cohort_cases["D"])

    # fires() legitimately returns RECIPIENT_FAMILIARITY/GRAPH_PROXIMITY here:
    # this is a genuinely first-time payment to a socially-unconnected
    # recipient, and both signals are structurally true regardless of amount
    # or hour. should_intervene() is the actual "silent pass" gate — per the
    # explicit design decision this codebase already made, structural-only
    # reasons never escalate on their own. See sentri/scorer/vector.py's
    # should_intervene() docstring.
    assert set(triggered) <= {TriggerReason.RECIPIENT_FAMILIARITY, TriggerReason.GRAPH_PROXIMITY}
    assert should_intervene(triggered) is False


async def test_cohort_E_high_trust_high_amount(cohort_cases: dict[str, dict[str, Any]]) -> None:
    vector, triggered = await _cohort_vector_and_triggered(cohort_cases["E"])

    assert TriggerReason.AMOUNT_Z_RECIPIENT in triggered
    assert TriggerReason.RECIPIENT_FAMILIARITY not in triggered
    assert vector.recipient_familiarity >= config.THRESHOLDS["recipient_familiarity_below"]


async def test_cohort_F_no_graph(cohort_cases: dict[str, dict[str, Any]]) -> None:
    vector, triggered = await _cohort_vector_and_triggered(cohort_cases["F"])

    assert TriggerReason.AMOUNT_Z_GLOBAL in triggered
    assert TriggerReason.RECIPIENT_FAMILIARITY in triggered
    assert TriggerReason.GRAPH_PROXIMITY not in triggered
    assert vector.graph_proximity is None


# ---------------------------------------------------------------------------
# score_recipient: familiarity
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 6, 1, 12, 0, tzinfo=_WAT)


def _frequent_recipient_rollup(
    recipient_id: str, now: datetime, count: int = 10
) -> RecipientRollup:
    txs = tuple(
        Transaction(
            amount_kobo=50_000, timestamp=now - timedelta(days=i), recipient_id=recipient_id
        )
        for i in range(count)
    )
    amounts = [tx.amount_kobo for tx in txs]
    return RecipientRollup(
        recipient_id=recipient_id,
        count=len(txs),
        mean_kobo=float(sum(amounts)) / len(amounts),
        std_kobo=0.0,
        min_kobo=min(amounts),
        max_kobo=max(amounts),
        first_seen=min(tx.timestamp for tx in txs),
        last_seen=max(tx.timestamp for tx in txs),
        total_volume_kobo=sum(amounts),
        transactions=txs,
    )


def _profile_with_recipients(
    recipients: dict[str, RecipientRollup], social_graph: SocialGraph | None = None
) -> UserProfile:
    return UserProfile(
        user_id="test_user",
        recipients=recipients,
        global_mean_kobo=50_000.0,
        global_std_kobo=5_000.0,
        hour_histogram=tuple([0] * 24),
        currencies_seen=frozenset({"NGN"}),
        social_graph=social_graph,
    )


def test_familiarity_is_high_for_known_frequent_recipient() -> None:
    rollup = _frequent_recipient_rollup("known_friend", _NOW, count=10)
    profile = _profile_with_recipients({"known_friend": rollup})
    event = TransactionEvent(
        amount_kobo=50_000,
        timestamp=_NOW.isoformat(),
        recipient_id="known_friend",
        user_id="test_user",
    )

    familiarity, _proximity = score_recipient(profile, event, _NOW)

    assert familiarity > 0.5


def test_familiarity_is_zero_for_unknown_recipient() -> None:
    profile = _profile_with_recipients({})
    event = TransactionEvent(
        amount_kobo=50_000, timestamp=_NOW.isoformat(), recipient_id="stranger", user_id="test_user"
    )

    familiarity, _proximity = score_recipient(profile, event, _NOW)

    assert familiarity == 0.0


# ---------------------------------------------------------------------------
# score_recipient: proximity
# ---------------------------------------------------------------------------


def _social_graph() -> SocialGraph:
    return SocialGraph(
        user_id="test_user",
        friends=frozenset({"direct_friend"}),
        friends_of_friends={"direct_friend": frozenset({"friend_of_friend"})},
    )


def test_proximity_is_none_when_social_graph_is_none() -> None:
    profile = _profile_with_recipients({}, social_graph=None)
    event = TransactionEvent(
        amount_kobo=1000, timestamp=_NOW.isoformat(), recipient_id="anyone", user_id="test_user"
    )

    _familiarity, proximity = score_recipient(profile, event, _NOW)

    assert proximity is None


def test_proximity_is_high_for_direct_friend() -> None:
    profile = _profile_with_recipients({}, social_graph=_social_graph())
    event = TransactionEvent(
        amount_kobo=1000,
        timestamp=_NOW.isoformat(),
        recipient_id="direct_friend",
        user_id="test_user",
    )

    _familiarity, proximity = score_recipient(profile, event, _NOW)

    assert proximity == 0.7


def test_proximity_is_moderate_for_friend_of_friend() -> None:
    profile = _profile_with_recipients({}, social_graph=_social_graph())
    event = TransactionEvent(
        amount_kobo=1000,
        timestamp=_NOW.isoformat(),
        recipient_id="friend_of_friend",
        user_id="test_user",
    )

    _familiarity, proximity = score_recipient(profile, event, _NOW)

    assert proximity == 0.4


def test_proximity_is_zero_for_stranger_with_graph_present() -> None:
    profile = _profile_with_recipients({}, social_graph=_social_graph())
    event = TransactionEvent(
        amount_kobo=1000, timestamp=_NOW.isoformat(), recipient_id="stranger", user_id="test_user"
    )

    _familiarity, proximity = score_recipient(profile, event, _NOW)

    assert proximity == 0.0


# ---------------------------------------------------------------------------
# score_amount
# ---------------------------------------------------------------------------


def _varied_rollup(recipient_id: str, count: int, now: datetime) -> RecipientRollup:
    """count transactions with distinct amounts, so std_kobo > 0."""
    amounts = [10_000 + i * 5_000 for i in range(count)]
    txs = tuple(
        Transaction(
            amount_kobo=amount, timestamp=now - timedelta(days=i), recipient_id=recipient_id
        )
        for i, amount in enumerate(amounts)
    )
    mean = sum(amounts) / len(amounts)
    variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
    return RecipientRollup(
        recipient_id=recipient_id,
        count=count,
        mean_kobo=mean,
        std_kobo=variance**0.5,
        min_kobo=min(amounts),
        max_kobo=max(amounts),
        first_seen=min(tx.timestamp for tx in txs),
        last_seen=max(tx.timestamp for tx in txs),
        total_volume_kobo=sum(amounts),
        transactions=txs,
    )


def _uniform_rollup(
    recipient_id: str, count: int, now: datetime, amount: int = 20_000
) -> RecipientRollup:
    """count transactions all at the same amount, so std_kobo == 0."""
    txs = tuple(
        Transaction(
            amount_kobo=amount, timestamp=now - timedelta(days=i), recipient_id=recipient_id
        )
        for i in range(count)
    )
    return RecipientRollup(
        recipient_id=recipient_id,
        count=count,
        mean_kobo=float(amount),
        std_kobo=0.0,
        min_kobo=amount,
        max_kobo=amount,
        first_seen=min(tx.timestamp for tx in txs),
        last_seen=max(tx.timestamp for tx in txs),
        total_volume_kobo=amount * count,
        transactions=txs,
    )


def test_score_amount_uses_recipient_z_when_enough_samples() -> None:
    assert Z_SCORE_MIN_SAMPLES >= 1
    rollup = _varied_rollup("recipient", Z_SCORE_MIN_SAMPLES, _NOW)
    profile = _profile_with_recipients({"recipient": rollup})
    event = TransactionEvent(
        amount_kobo=100_000,
        timestamp=_NOW.isoformat(),
        recipient_id="recipient",
        user_id="test_user",
    )

    result = score_amount(profile, event)

    assert result["amount_z_recipient"] is not None
    assert result["z_score_path"] == "recipient_z"


def test_score_amount_falls_back_to_global_with_too_few_samples() -> None:
    count = max(Z_SCORE_MIN_SAMPLES - 1, 0)
    rollup = _varied_rollup("recipient", max(count, 1), _NOW)
    # Force the sample count below the threshold regardless of how many
    # transactions were needed to build a non-degenerate rollup.
    rollup = RecipientRollup(**{**rollup.__dict__, "count": count})
    profile = _profile_with_recipients({"recipient": rollup})
    event = TransactionEvent(
        amount_kobo=100_000,
        timestamp=_NOW.isoformat(),
        recipient_id="recipient",
        user_id="test_user",
    )

    result = score_amount(profile, event)

    assert result["amount_z_recipient"] is None
    assert result["z_score_path"] == "global_z_min_samples"


def test_score_amount_falls_back_to_global_on_zero_variance() -> None:
    rollup = _uniform_rollup("recipient", Z_SCORE_MIN_SAMPLES, _NOW)
    profile = _profile_with_recipients({"recipient": rollup})
    event = TransactionEvent(
        amount_kobo=100_000,
        timestamp=_NOW.isoformat(),
        recipient_id="recipient",
        user_id="test_user",
    )

    result = score_amount(profile, event)

    assert result["amount_z_recipient"] is None
    assert result["z_score_path"] == "global_z_zero_variance"


def test_score_amount_treats_floating_point_near_zero_std_as_zero_variance() -> None:
    rollup = _uniform_rollup("recipient", Z_SCORE_MIN_SAMPLES, _NOW)
    # Floating-point drift on repeated identical amounts can leave std_kobo at
    # something like 1e-15 rather than exact 0.0; the scorer's tolerance check
    # must still route this to the global fallback rather than dividing by it.
    rollup = RecipientRollup(**{**rollup.__dict__, "std_kobo": 1e-15})
    profile = _profile_with_recipients({"recipient": rollup})
    event = TransactionEvent(
        amount_kobo=100_000,
        timestamp=_NOW.isoformat(),
        recipient_id="recipient",
        user_id="test_user",
    )

    result = score_amount(profile, event)

    assert result["amount_z_recipient"] is None
    assert result["z_score_path"] == "global_z_zero_variance"


# ---------------------------------------------------------------------------
# score_hour
# ---------------------------------------------------------------------------


def _histogram_peaked_at(hour: int, count: int = 100) -> tuple[int, ...]:
    histogram = [0] * 24
    histogram[hour] = count
    return tuple(histogram)


def test_score_hour_wraps_around_midnight() -> None:
    """00:00 should read as near the user's typical 23:00, not maximally different."""
    profile = _profile_with_recipients({}, social_graph=None)
    profile = UserProfile(**{**profile.__dict__, "hour_histogram": _histogram_peaked_at(23)})
    event_at_midnight = TransactionEvent(
        amount_kobo=1000,
        timestamp=datetime(2026, 6, 1, 0, 0, tzinfo=_WAT).isoformat(),
        recipient_id="anyone",
        user_id="test_user",
    )

    deviation = score_hour(profile, event_at_midnight)

    assert deviation == pytest.approx(0.0170, abs=0.01)


def test_score_hour_is_maximal_at_the_opposite_hour() -> None:
    """11:00 is 12 hours from a 23:00 peak - the true cyclical opposite."""
    profile = _profile_with_recipients({}, social_graph=None)
    profile = UserProfile(**{**profile.__dict__, "hour_histogram": _histogram_peaked_at(23)})
    event_at_opposite_hour = TransactionEvent(
        amount_kobo=1000,
        timestamp=datetime(2026, 6, 1, 11, 0, tzinfo=_WAT).isoformat(),
        recipient_id="anyone",
        user_id="test_user",
    )

    deviation = score_hour(profile, event_at_opposite_hour)

    assert deviation == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# fires(): each dimension fires independently
# ---------------------------------------------------------------------------


def _baseline_vector(**overrides: Any) -> DeviationVector:
    """A DeviationVector that fires on nothing under default THRESHOLDS."""
    fields: dict[str, Any] = {
        "recipient_familiarity": 1.0,
        "graph_proximity": None,
        "amount_z_recipient": None,
        "amount_z_global": 0.0,
        "amount_drift_ratio": None,
        "hour_deviation": 0.0,
        "currency_novelty": False,
        "cross_border": False,
        "z_score_path": "global_z_min_samples",
    }
    fields.update(overrides)
    return DeviationVector(**fields)


@pytest.mark.parametrize(
    ("overrides", "expected_reason"),
    [
        ({"recipient_familiarity": 0.0}, TriggerReason.RECIPIENT_FAMILIARITY),
        ({"graph_proximity": 0.0}, TriggerReason.GRAPH_PROXIMITY),
        ({"amount_z_recipient": 10.0}, TriggerReason.AMOUNT_Z_RECIPIENT),
        ({"amount_z_global": 10.0}, TriggerReason.AMOUNT_Z_GLOBAL),
        ({"amount_drift_ratio": 5.0}, TriggerReason.AMOUNT_DRIFT),
        ({"hour_deviation": 0.9}, TriggerReason.HOUR_DEVIATION),
        ({"currency_novelty": True}, TriggerReason.CURRENCY_NOVELTY),
        ({"cross_border": True}, TriggerReason.CROSS_BORDER),
    ],
)
def test_fires_triggers_exactly_one_dimension_at_a_time(
    overrides: dict[str, Any], expected_reason: TriggerReason
) -> None:
    vector = _baseline_vector(**overrides)

    triggered = fires(vector, config.THRESHOLDS)

    assert triggered == [expected_reason]


def test_fires_returns_empty_for_baseline_vector() -> None:
    vector = _baseline_vector()

    triggered = fires(vector, config.THRESHOLDS)

    assert triggered == []


# ---------------------------------------------------------------------------
# should_intervene()
# ---------------------------------------------------------------------------


def test_should_intervene_is_false_for_empty_triggered() -> None:
    assert should_intervene([]) is False


def test_should_intervene_is_true_for_a_substantive_reason() -> None:
    assert should_intervene([TriggerReason.AMOUNT_Z_GLOBAL]) is True


def test_should_intervene_is_false_for_structural_reasons_only() -> None:
    # This is the deliberate design this codebase settled on: familiarity and
    # proximity fire for every first-time, unconnected recipient regardless
    # of anomaly, so they can't justify escalation alone. See
    # sentri/scorer/vector.py's should_intervene() docstring, and
    # test_cohort_D_baseline above for the end-to-end case this protects.
    assert (
        should_intervene([TriggerReason.RECIPIENT_FAMILIARITY, TriggerReason.GRAPH_PROXIMITY])
        is False
    )


def test_should_intervene_is_true_when_structural_and_substantive_both_fire() -> None:
    assert (
        should_intervene([TriggerReason.RECIPIENT_FAMILIARITY, TriggerReason.AMOUNT_Z_RECIPIENT])
        is True
    )
