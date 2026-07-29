"""Real BMONI adapter, calling the embedded-dev sandbox over HTTP.

Ground truth (BMONI Hackathon Quick Start, restated 2026-07-29) that this
module relies on:

- Base URL is https://embedded-dev.bmoni.com; every documented path already
  starts with /v1, so this client never adds another /v1 prefix.
- Auth on every request: header x-api-key: <BMONI_API_KEY>, plus
  Content-Type: application/json.
- Reads: GET /v1/users/{userId}/smart-wallets/account/transactions and
  .../account/balances.
- Transfers (confirmed spec, Prompt 13): POST
  /v1/users/{userId}/withdrawal/wallet/nigeria (bank payout) or
  .../withdrawal/smart-wallet/crypto (on-chain payout) each return
  {proposalId, signPayload} in one call. The payload is EIP-712 typed data,
  signed server-side with eth_account.Account.sign_typed_data (see
  sentri.bmoni.signing for where the keypair comes from), then POST
  /v1/users/{userId}/smart-wallets/proposals/{proposalId}/sign with
  {signature}. BMONI's KMS co-signature is appended automatically
  server-side -- nothing further is needed from us.
- No documented endpoints exist for a social graph, a decision-log
  write-back, or a transfer-intent pre-authorization hook. Those methods are
  therefore deliberate no-ops here (not network calls that would always
  404/fail) so the rest of the pipeline degrades the same way it already does
  for a stub with no social graph.

The response schema for transactions/balances isn't confirmed by any doc:
every real response is logged at DEBUG so it can be inspected against a live
sandbox call, and the field mapping below is a best guess pending that.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

import httpx
from eth_account import Account
from eth_account.signers.local import LocalAccount

from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import Config
from sentri.models.profile import SocialGraph
from sentri.models.transaction import Transaction

logger = logging.getLogger(__name__)

DestinationType = Literal["nigeria", "crypto"]


class BMONITransferError(RuntimeError):
    """Raised when a live withdrawal proposal, its signing, or submission fails.

    Unlike the read methods below, transfer() never swallows failures into an
    empty/None result: moving real (if tiny, sandbox) funds must fail loudly.
    """


def _parse_transaction(raw: dict[str, Any]) -> Optional[Transaction]:
    """Map a raw BMONI transaction record onto the canonical Transaction type.

    TODO(bmoni-schema): confirm these field names and the amount's precision
    against a live sandbox response (see module docstring). Defaulting to
    decimal-naira amounts (e.g. "1000.00"), matching how the quick-start doc
    itself quotes amounts, not kobo-style integers or raw 18-decimal token
    units.
    """
    try:
        raw_amount = raw["amount"]
        amount_kobo = round(float(raw_amount) * 100)
        timestamp = ingest_timestamp(raw["timestamp"])
        recipient_id = raw.get("recipientId") or raw.get("counterparty") or "unknown"
        return Transaction(
            amount_kobo=amount_kobo,
            timestamp=timestamp,
            recipient_id=recipient_id,
            currency=raw.get("currency", "CNGN"),
            memo=raw.get("memo"),
        )
    except (KeyError, TypeError, ValueError):
        logger.warning("Skipping unparseable BMONI transaction record: %r", raw, exc_info=True)
        return None


class BMONIClient:
    """Structurally implements sentri.bmoni.protocol.BMONIClient against the real sandbox.

    get_balance is an extra read method the sandbox exposes; it isn't part of
    the protocol because nothing in the scoring pipeline consumes it yet.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if http_client is not None:
            self._client = http_client
            return

        resolved_key = api_key if api_key is not None else Config.BMONI_API_KEY
        if not resolved_key:
            raise ValueError(
                "BMONI_API_KEY is required to construct a real BMONIClient "
                "(set it in the environment or pass api_key explicitly)"
            )

        self._client = httpx.AsyncClient(
            base_url=base_url or Config.BMONI_BASE_URL,
            headers={"x-api-key": resolved_key, "Content-Type": "application/json"},
        )

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        try:
            response = await self._client.get(
                f"/v1/users/{user_id}/smart-wallets/account/transactions"
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.warning(
                "BMONI get_transaction_history failed for user_id=%s", user_id, exc_info=True
            )
            return []

        payload = response.json()
        logger.debug("BMONI raw transaction history response for user_id=%s: %r", user_id, payload)

        records = payload.get("transactions", []) if isinstance(payload, dict) else payload
        parsed = (_parse_transaction(record) for record in records)
        return [transaction for transaction in parsed if transaction is not None]

    async def get_balance(self, user_id: str) -> Optional[dict[str, Any]]:
        try:
            response = await self._client.get(f"/v1/users/{user_id}/smart-wallets/account/balances")
            response.raise_for_status()
        except httpx.HTTPError:
            logger.warning("BMONI get_balance failed for user_id=%s", user_id, exc_info=True)
            return None

        payload: dict[str, Any] = response.json()
        logger.debug("BMONI raw balance response for user_id=%s: %r", user_id, payload)
        return payload

    async def transfer(
        self,
        user_id: str,
        signer: LocalAccount,
        amount_kobo: int,
        destination: dict[str, Any],
        destination_type: DestinationType = "nigeria",
    ) -> dict[str, Any]:
        """Execute a live withdrawal end-to-end: propose, sign server-side, submit.

        `destination` carries whatever fields the payout rail needs (bank
        account details for "nigeria", a wallet address for "crypto") and is
        passed through to the proposal request as-is.

        `signer` is the demo identity's server-held keypair (see
        sentri.bmoni.signing) -- the same one that owns the smart wallet,
        since the owner address is fixed at wallet-creation time.

        TODO(bmoni-schema): the proposal request body's exact field names are
        a best guess (amount as a decimal-naira float, destination fields
        merged in directly); confirm against the first live response.
        """
        proposal_path = (
            f"/v1/users/{user_id}/withdrawal/wallet/nigeria"
            if destination_type == "nigeria"
            else f"/v1/users/{user_id}/withdrawal/smart-wallet/crypto"
        )

        try:
            proposal_response = await self._client.post(
                proposal_path,
                json={"amount": amount_kobo / 100, **destination},
            )
            proposal_response.raise_for_status()
        except httpx.HTTPError as exc:
            raise BMONITransferError(f"withdrawal proposal request failed: {exc}") from exc

        proposal = proposal_response.json()
        logger.debug("BMONI raw withdrawal-proposal response for user_id=%s: %r", user_id, proposal)

        try:
            proposal_id = proposal["proposalId"]
            sign_payload = proposal["signPayload"]
        except KeyError as exc:
            raise BMONITransferError(
                f"withdrawal proposal response missing {exc}: {proposal!r}"
            ) from exc

        signed = Account.sign_typed_data(signer.key, full_message=sign_payload)

        try:
            sign_response = await self._client.post(
                f"/v1/users/{user_id}/smart-wallets/proposals/{proposal_id}/sign",
                json={"signature": signed.signature.hex()},
            )
            sign_response.raise_for_status()
        except httpx.HTTPError as exc:
            raise BMONITransferError(f"proposal signature submission failed: {exc}") from exc

        result: dict[str, Any] = sign_response.json()
        logger.debug("BMONI raw proposal-sign response for user_id=%s: %r", user_id, result)
        return result

    async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]:
        """No social-graph/friends endpoint is documented; returning None here
        makes graph.proximity.proximity() treat this the same as any other
        user with no exposed graph -- a missingness mask (never None literal
        0.0), so GRAPH_PROXIMITY simply never fires rather than firing on a
        false "no connection" reading. See sentri/graph/proximity.py."""
        return None

    async def on_transfer_intent_hook(self, callback: Any) -> None:
        """No transfer-intent pre-authorization hook is documented yet."""
        return None

    async def aclose(self) -> None:
        await self._client.aclose()
