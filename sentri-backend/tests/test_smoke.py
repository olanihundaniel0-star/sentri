"""Top-level smoke tests: package sanity, plus one pass through the full pipeline
(seed data -> profile -> scorer -> template synthesizer) for a normal and an
anomalous transaction. No network/LLM calls anywhere in this file.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sentri import __version__, config
from sentri.api.deps import TemplateOnlySynthesizer
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.graph.builder import build_profile
from sentri.models.profile import UserProfile
from sentri.models.transaction import TransactionEvent
from sentri.scorer.vector import build_vector, fires, should_intervene
from seeds.generator import write_seed_data

_WAT = ZoneInfo("Africa/Lagos")


def test_package_importable() -> None:
    assert __version__ == "0.1.0"


def test_config_defaults() -> None:
    assert config.FAMILIARITY_DECAY_LAMBDA == 0.01
    assert config.DEFAULT_LANGUAGE == "en"
    assert "recipient_familiarity_below" in config.THRESHOLDS


def test_seed_data_fixture(seed_data: dict) -> None:
    assert isinstance(seed_data, dict)


async def _build_user_001_profile() -> UserProfile:
    write_seed_data()
    stub = InMemoryBMONIStub()
    transactions = await stub.get_transaction_history("user_001")
    social_graph = await stub.get_social_graph("user_001")
    return build_profile("user_001", transactions, social_graph)


def _mode_hour(histogram: tuple[int, ...]) -> int:
    return max(range(24), key=lambda hour: histogram[hour])


async def test_normal_transaction_is_silent_pass() -> None:
    profile = await _build_user_001_profile()

    landlord_id = "user_001_landlord"
    rollup = profile.recipients[landlord_id]
    hour = _mode_hour(profile.hour_histogram)

    # Anchor well past the recipient's own transaction history (rather than
    # "today") so the amount-drift 30/60-day windows see no transactions and
    # stay None. Using real wall-clock "now" here would make this test's
    # outcome depend on the calendar date it happens to run on.
    last_seen = max(
        tx.timestamp for rollup_ in profile.recipients.values() for tx in rollup_.transactions
    )
    now = (
        (last_seen + timedelta(days=200))
        .astimezone(_WAT)
        .replace(hour=hour, minute=0, second=0, microsecond=0)
    )

    event = TransactionEvent(
        amount_kobo=round(rollup.mean_kobo),
        timestamp=now.isoformat(),
        recipient_id=landlord_id,
        currency="NGN",
        user_id="user_001",
        cross_border=False,
    )

    vector = build_vector(profile, event, now)
    triggered = fires(vector, config.THRESHOLDS)

    assert should_intervene(triggered) is False


async def test_anomalous_transaction_is_intervene() -> None:
    profile = await _build_user_001_profile()

    now = datetime.now(_WAT)
    event = TransactionEvent(
        amount_kobo=5_000_000,
        timestamp=now.isoformat(),
        recipient_id="user_001_unknown_offshore_agent",
        currency="XYZ",
        user_id="user_001",
        cross_border=True,
    )

    vector = build_vector(profile, event, now)
    triggered = fires(vector, config.THRESHOLDS)
    assert should_intervene(triggered) is True

    synthesizer = TemplateOnlySynthesizer()
    explanation, synthesizer_used = await synthesizer.synthesize(
        vector, {"currency": event.currency}, triggered, "en"
    )

    assert synthesizer_used == "template"
    assert explanation != ""
