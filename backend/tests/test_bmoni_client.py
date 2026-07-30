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
    "signingPayloadHash": "0x" + "ab" * 32,
    "typedData": {
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
    },
    "signatureExpiresAt": "2026-07-31T01:20:30.101Z",
    "proposalStatus": "PENDING_SIGNATURES",
}


def _make_client() -> BMONIClient:
    return BMONIClient(api_key="test-key", base_url=_BASE_URL)


def _mock_balances(wallet_ids: list[str]) -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/balances").mock(
        return_value=httpx.Response(
            200,
            json={
                "smartAccountAddress": "0xabc",
                "balances": [
                    {"smartWalletId": wallet_id, "currency": "NGN", "balance": "0", "error": None}
                    for wallet_id in wallet_ids
                ],
            },
        )
    )


def test_missing_api_key_raises() -> None:
    with pytest.raises(ValueError):
        BMONIClient(api_key=None, base_url=_BASE_URL)


@respx.mock
async def test_get_transaction_history_happy_path_maps_to_canonical_transaction() -> None:
    _mock_balances(["wallet-1"])
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-1/transactions").mock(
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
async def test_get_transaction_history_fans_out_over_every_wallet() -> None:
    """A user with multiple currency wallets (e.g. NGN and USDB) gets
    transactions from all of them concatenated."""
    _mock_balances(["wallet-ngn", "wallet-usdb"])
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-ngn/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [
                    {
                        "amount": "1000.00",
                        "timestamp": "2026-01-15T12:00:00+00:00",
                        "recipientId": "user_002",
                    }
                ]
            },
        )
    )
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-usdb/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [
                    {
                        "amount": "10.00",
                        "timestamp": "2026-01-16T12:00:00+00:00",
                        "recipientId": "user_003",
                    }
                ]
            },
        )
    )

    client = _make_client()
    history = await client.get_transaction_history("user_001")

    assert {tx.recipient_id for tx in history} == {"user_002", "user_003"}


@respx.mock
async def test_get_transaction_history_skips_unparseable_records() -> None:
    _mock_balances(["wallet-1"])
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-1/transactions").mock(
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
async def test_get_transaction_history_no_wallets_returns_empty(
    caplog: pytest.LogCaptureFixture,
) -> None:
    _mock_balances([])

    client = _make_client()
    history = await client.get_transaction_history("user_001")

    assert history == []


@respx.mock
async def test_get_transaction_history_balances_timeout_falls_back_to_empty_and_warns(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/account/balances").mock(
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
    _mock_balances(["wallet-1"])
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-1/transactions").mock(
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
    _mock_balances(["wallet-1"])
    respx.get(f"{_BASE_URL}/v1/users/user_001/smart-wallets/wallet-1/transactions").mock(
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
        destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
    )

    assert result == {"status": "submitted"}
    assert proposal_route.called
    assert sign_route.called
    sent_signature = json.loads(sign_route.calls[0].request.content)["signature"]
    assert sent_signature.startswith("0x")
    assert len(sent_signature.removeprefix("0x")) == 130  # 65-byte ECDSA signature, hex-encoded


@respx.mock
async def test_transfer_amount_kobo_always_wins_over_a_destination_amount_key() -> None:
    """destination is caller-supplied; it must never be able to change what
    amount BMONI actually moves once amount_kobo has been scored. Build a
    destination carrying its own conflicting "fromAmount" and assert the
    request body still reflects amount_kobo, not destination's value."""
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
            "sourceSmartWalletId": "wallet-1",
            "bankAccountId": "bank-acct-1",
            "fromAmount": "5000000.00",
        },
    )

    sent_body = json.loads(proposal_route.calls[0].request.content)
    assert sent_body["fromAmount"] == "1000.00"
    assert sent_body["bankAccountId"] == "bank-acct-1"


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
        destination={
            "sourceSmartWalletId": "wallet-1",
            "destinationChain": "Base",
            "destinationCurrency": "USDC",
            "destinationAddress": "0xabc",
        },
        destination_type="crypto",
    )

    assert proposal_route.called
    sent_body = json.loads(proposal_route.calls[0].request.content)
    assert sent_body["amount"] == "1000.00"
    assert sent_body["destinationAddress"] == "0xabc"


@respx.mock
async def test_transfer_raises_when_sign_payload_pending() -> None:
    """signPayloadPending means the upstream hasn't prepared the EIP-712
    payload synchronously; no polling endpoint is implemented yet, so this
    must fail loudly rather than silently returning something unsigned."""
    respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(
            200,
            json={
                "proposalId": "prop-1",
                "signPayloadPending": True,
                "signPayloadHint": "poll GET .../sign-payload",
            },
        )
    )

    client = _make_client()
    with pytest.raises(BMONITransferError):
        await client.transfer(
            user_id="user_001",
            signer=Account.create(),
            amount_kobo=100_000,
            destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
        )


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
            destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
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
            destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
        )


@respx.mock
async def test_transfer_raises_when_sign_payload_missing_signing_hash() -> None:
    """signPayload is a wrapper -- {signingPayloadHash, typedData,
    signatureExpiresAt, proposalStatus} -- confirmed live against the
    sandbox 2026-07-30. The sandbox signs/verifies signingPayloadHash
    directly (a raw ecrecover), not typedData (see module docstring for the
    live 400 this produced before that was discovered); a malformed/
    incomplete wrapper missing signingPayloadHash must still fail loudly
    with BMONITransferError, not a bare KeyError."""
    respx.post(f"{_BASE_URL}/v1/users/user_001/withdrawal/wallet/nigeria").mock(
        return_value=httpx.Response(
            200,
            json={
                "proposalId": "prop-1",
                "signPayload": {
                    "typedData": _EIP712_SIGN_PAYLOAD["typedData"],
                    "signatureExpiresAt": "2026-07-31T01:20:30.101Z",
                    "proposalStatus": "PENDING_SIGNATURES",
                },
            },
        )
    )

    client = _make_client()
    with pytest.raises(BMONITransferError):
        await client.transfer(
            user_id="user_001",
            signer=Account.create(),
            amount_kobo=100_000,
            destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
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
            destination={"sourceSmartWalletId": "wallet-1", "bankAccountId": "bank-acct-1"},
        )
