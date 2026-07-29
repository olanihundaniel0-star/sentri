"""Mock-based tests for the real BMONI HTTP adapter. Never hits the live sandbox."""

from __future__ import annotations

import json
import logging

import httpx
import pytest
import respx
from eth_account import Account

from sentri.bmoni.client import BMONIClient, BMONITransferError

_BASE_URL = "https://embedded-dev.bmoni.com"

_EIP712_SIGN_PAYLOAD = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
        ],
        "Withdrawal": [
            {"name": "amount", "type": "uint256"},
        ],
    },
    "domain": {"name": "BMONI", "version": "1", "chainId": 1},
    "primaryType": "Withdrawal",
    "message": {"amount": 1000},
}


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
async def test_get_transaction_history_malformed_response_falls_back_to_empty_and_warns(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A 200 response whose body is neither a dict nor a list (e.g. a bare
    JSON number) must degrade the same way a failed HTTP call already does,
    not raise an uncaught TypeError out of the method."""
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/transactions").mock(
        return_value=httpx.Response(200, json=42)
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


async def test_on_transfer_intent_hook_is_a_noop() -> None:
    await _make_client().on_transfer_intent_hook(lambda *_: None)


@respx.mock
async def test_transfer_happy_path_proposes_signs_and_submits() -> None:
    signer = Account.create()
    proposal_route = respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(
            200, json={"proposalId": "prop-1", "signPayload": _EIP712_SIGN_PAYLOAD}
        )
    )
    sign_route = respx.post(
        f"{_BASE_URL}/v1/users/user_001/smart-wallets/proposals/prop-1/sign"
    ).mock(return_value=httpx.Response(200, json={"status": "submitted"}))

    client = _make_client()
    result = await client.transfer(
        user_id="user_001",
        signer=signer,
        amount_kobo=100_000,
        destination={"accountNumber": "0001112222", "bankCode": "044"},
    )

    assert result == {"status": "submitted"}
    assert proposal_route.called
    assert sign_route.called
    sent_signature = json.loads(sign_route.calls[0].request.content)["signature"]
    assert len(sent_signature.removeprefix("0x")) == 130  # 65-byte ECDSA signature, hex-encoded


@respx.mock
async def test_transfer_amount_kobo_always_wins_over_a_destination_amount_key() -> None:
    """destination is caller-supplied; it must never be able to change what
    amount BMONI actually moves once amount_kobo has been scored. Build a
    destination carrying its own conflicting "amount" and assert the request
    body still reflects amount_kobo, not destination's value."""
    proposal_route = respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(
            200, json={"proposalId": "prop-1", "signPayload": _EIP712_SIGN_PAYLOAD}
        )
    )
    respx.post(f"{_BASE_URL}/v1/users/user_001/smart-wallets/proposals/prop-1/sign").mock(
        return_value=httpx.Response(200, json={"status": "submitted"})
    )

    client = _make_client()
    await client.transfer(
        user_id="user_001",
        signer=Account.create(),
        amount_kobo=100_000,
        destination={
            "accountNumber": "0001112222",
            "bankCode": "044",
            "amount": 500_000_000,
        },
    )

    sent_body = json.loads(proposal_route.calls[0].request.content)
    assert sent_body["amount"] == 1000.0
    assert sent_body["accountNumber"] == "0001112222"


@respx.mock
async def test_transfer_uses_crypto_endpoint_for_crypto_destination() -> None:
    signer = Account.create()
    proposal_route = respx.post(
        f"{_BASE_URL}/v1/users/user_001/withdrawal/smart-wallet/crypto"
    ).mock(
        return_value=httpx.Response(
            200, json={"proposalId": "prop-2", "signPayload": _EIP712_SIGN_PAYLOAD}
        )
    )
    respx.post(f"{_BASE_URL}/v1/users/user_001/smart-wallets/proposals/prop-2/sign").mock(
        return_value=httpx.Response(200, json={"status": "submitted"})
    )

    client = _make_client()
    await client.transfer(
        user_id="user_001",
        signer=signer,
        amount_kobo=100_000,
        destination={"address": "0xabc"},
        destination_type="crypto",
    )

    assert proposal_route.called


@respx.mock
async def test_transfer_raises_on_proposal_request_failure() -> None:
    respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    client = _make_client()
    with pytest.raises(BMONITransferError):
        await client.transfer(
            user_id="user_001",
            signer=Account.create(),
            amount_kobo=100_000,
            destination={"accountNumber": "0001112222", "bankCode": "044"},
        )


@respx.mock
async def test_transfer_raises_when_proposal_response_missing_fields() -> None:
    respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(200, json={"unexpected": "shape"})
    )

    client = _make_client()
    with pytest.raises(BMONITransferError):
        await client.transfer(
            user_id="user_001",
            signer=Account.create(),
            amount_kobo=100_000,
            destination={"accountNumber": "0001112222", "bankCode": "044"},
        )


@respx.mock
async def test_transfer_raises_on_sign_submission_failure() -> None:
    respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(
            200, json={"proposalId": "prop-1", "signPayload": _EIP712_SIGN_PAYLOAD}
        )
    )
    respx.post(f"{_BASE_URL}/v1/users/user_001/smart-wallets/proposals/prop-1/sign").mock(
        return_value=httpx.Response(400, json={"error": "bad signature"})
    )

    client = _make_client()
    with pytest.raises(BMONITransferError):
        await client.transfer(
            user_id="user_001",
            signer=Account.create(),
            amount_kobo=100_000,
            destination={"accountNumber": "0001112222", "bankCode": "044"},
        )
