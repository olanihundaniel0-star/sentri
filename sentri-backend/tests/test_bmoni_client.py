"""Mock-based tests for the real BMONI HTTP adapter. Never hits the live sandbox."""

from __future__ import annotations

import logging

import httpx
import pytest
import respx

from sentri.bmoni.client import BMONIClient

_BASE_URL = "https://embedded-dev.bmoni.com"


def _make_client() -> BMONIClient:
    return BMONIClient(api_key="test-key", base_url=_BASE_URL)


def test_missing_api_key_raises() -> None:
    with pytest.raises(ValueError):
        BMONIClient(api_key=None, base_url=_BASE_URL)


@respx.mock
async def test_get_transaction_history_happy_path_maps_to_canonical_transaction() -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [
                    {
                        "amount": "1000.00",
                        "timestamp": "2026-01-15T12:00:00+00:00",
                        "recipientId": "user_002",
                        "currency": "CNGN",
                        "memo": "lunch",
                    }
                ]
            },
        )
    )

    client = _make_client()
    history = await client.get_transaction_history("user_001")

    assert len(history) == 1
    assert history[0].amount_kobo == 100_000
    assert history[0].recipient_id == "user_002"
    assert history[0].currency == "CNGN"
    assert history[0].memo == "lunch"


@respx.mock
async def test_get_transaction_history_skips_unparseable_records() -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [
                    {"amount": "not-a-number", "timestamp": "2026-01-15T12:00:00+00:00"},
                    {
                        "amount": "50.00",
                        "timestamp": "2026-01-15T12:00:00+00:00",
                        "recipientId": "user_003",
                    },
                ]
            },
        )
    )

    client = _make_client()
    history = await client.get_transaction_history("user_001")

    assert len(history) == 1
    assert history[0].recipient_id == "user_003"


@respx.mock
async def test_get_transaction_history_timeout_falls_back_to_empty_and_warns(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/transactions").mock(
        side_effect=httpx.TimeoutException("timed out")
    )

    client = _make_client()
    with caplog.at_level(logging.WARNING, logger="sentri.bmoni.client"):
        history = await client.get_transaction_history("user_001")

    assert history == []
    assert any("get_transaction_history failed" in r.getMessage() for r in caplog.records)


@respx.mock
async def test_get_transaction_history_non_2xx_falls_back_to_empty_and_warns(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/transactions").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    client = _make_client()
    with caplog.at_level(logging.WARNING, logger="sentri.bmoni.client"):
        history = await client.get_transaction_history("user_001")

    assert history == []
    assert any("get_transaction_history failed" in r.getMessage() for r in caplog.records)


@respx.mock
async def test_get_balance_non_2xx_returns_none() -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/balances").mock(
        return_value=httpx.Response(404, json={"error": "not found"})
    )

    client = _make_client()
    assert await client.get_balance("user_001") is None


@respx.mock
async def test_get_balance_happy_path_returns_raw_payload() -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/balances").mock(
        return_value=httpx.Response(200, json={"CNGN": "1000.00"})
    )

    client = _make_client()
    assert await client.get_balance("user_001") == {"CNGN": "1000.00"}


async def test_get_social_graph_is_none() -> None:
    assert await _make_client().get_social_graph("user_001") is None


async def test_log_decision_is_a_noop() -> None:
    await _make_client().log_decision("user_001", "evt-1", "silent_pass", None)


async def test_on_transfer_intent_hook_is_a_noop() -> None:
    await _make_client().on_transfer_intent_hook(lambda *_: None)
