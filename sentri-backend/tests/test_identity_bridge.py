"""Tests for the synthetic-seed <-> real-BMONI identity bridge."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pytest

from sentri.bmoni.identity_bridge import fetch_live_event_for_bridged_user, real_bmoni_user_id
from sentri.models.profile import SocialGraph
from sentri.models.transaction import Transaction


class _FakeRealClient:
    """Stand-in for a real sentri.bmoni.client.BMONIClient in tests."""

    def __init__(self, transactions_by_id: dict[str, list[Transaction]]) -> None:
        self._transactions_by_id = transactions_by_id
        self.requested_user_ids: list[str] = []

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        self.requested_user_ids.append(user_id)
        return self._transactions_by_id.get(user_id, [])

    async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]:
        raise AssertionError("get_social_graph should not be called by the identity bridge")

    async def log_decision(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("log_decision should not be called by the identity bridge")

    async def on_transfer_intent_hook(self, callback: object) -> None:
        raise AssertionError("on_transfer_intent_hook should not be called by the identity bridge")


def test_shipped_bridge_placeholders_resolve_to_none() -> None:
    """seeds/identity_bridge.json ships with REPLACE_ placeholders until the
    onboarding script has actually been run for each identity."""
    assert real_bmoni_user_id("user_001") is None
    assert real_bmoni_user_id("user_002") is None


def test_unbridged_user_resolves_to_none() -> None:
    assert real_bmoni_user_id("user_003") is None


def test_real_bmoni_user_id_reads_a_filled_in_bridge_file(tmp_path: Path) -> None:
    bridge_path = tmp_path / "identity_bridge.json"
    bridge_path.write_text(
        json.dumps({"user_001": {"bmoni_user_id": "bmoni-abc123"}}), encoding="utf-8"
    )

    assert real_bmoni_user_id("user_001", bridge_path=bridge_path) == "bmoni-abc123"
    assert real_bmoni_user_id("user_002", bridge_path=bridge_path) is None


async def test_fetch_live_event_returns_none_when_user_not_bridged(tmp_path: Path) -> None:
    bridge_path = tmp_path / "identity_bridge.json"
    bridge_path.write_text("{}", encoding="utf-8")
    client = _FakeRealClient({})

    result = await fetch_live_event_for_bridged_user("user_001", client, bridge_path=bridge_path)

    assert result is None
    assert client.requested_user_ids == []


async def test_fetch_live_event_returns_none_when_no_live_history(tmp_path: Path) -> None:
    bridge_path = tmp_path / "identity_bridge.json"
    bridge_path.write_text(
        json.dumps({"user_001": {"bmoni_user_id": "bmoni-abc123"}}), encoding="utf-8"
    )
    client = _FakeRealClient({})

    result = await fetch_live_event_for_bridged_user("user_001", client, bridge_path=bridge_path)

    assert result is None
    assert client.requested_user_ids == ["bmoni-abc123"]


async def test_fetch_live_event_maps_latest_transaction_back_to_seed_user_id(
    tmp_path: Path,
) -> None:
    bridge_path = tmp_path / "identity_bridge.json"
    bridge_path.write_text(
        json.dumps({"user_001": {"bmoni_user_id": "bmoni-abc123"}}), encoding="utf-8"
    )
    older = Transaction(
        amount_kobo=100_000,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        recipient_id="user_999",
    )
    newer = Transaction(
        amount_kobo=250_000,
        timestamp=datetime(2026, 6, 1, tzinfo=timezone.utc),
        recipient_id="user_888",
        currency="CNGN",
    )
    client = _FakeRealClient({"bmoni-abc123": [older, newer]})

    result = await fetch_live_event_for_bridged_user("user_001", client, bridge_path=bridge_path)

    assert result is not None
    assert result.user_id == "user_001"
    assert result.amount_kobo == 250_000
    assert result.recipient_id == "user_888"
    assert result.currency == "CNGN"


@pytest.mark.parametrize("seed_user_id", ["user_001", "user_002"])
def test_shipped_bridge_notes_match_expected_cohorts(seed_user_id: str) -> None:
    from sentri.bmoni.identity_bridge import _load_bridge

    entry = _load_bridge()[seed_user_id]
    expected_cohort = {"user_001": "A", "user_002": "D"}[seed_user_id]
    assert entry["cohort"] == expected_cohort
