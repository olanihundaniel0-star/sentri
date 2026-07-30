"""Real BMONI adapter, calling the embedded-dev sandbox over HTTP.

Ground truth confirmed 2026-07-29/30 against the live sandbox's own OpenAPI
spec (GET /docs/openapi.json, rendered at /docs) and by driving each call for
real -- this superseded the original hackathon-doc guesses below, which were
wrong in several field names (see git history on this file for what changed
and why):

- Base URL is https://embedded-dev.bmoni.com; every documented path already
  starts with /v1, so this client never adds another /v1 prefix.
- Auth on every request: header x-api-key: <BMONI_API_KEY>, plus
  Content-Type: application/json.
- Reads: GET /v1/users/{userId}/smart-wallets/{smartWalletId}/transactions
  (paginated, {"transactions": [...]}; smartWalletId is per-currency and
  comes from a balances entry -- there is no user-wide transactions
  endpoint) and GET /v1/users/{userId}/smart-wallets/account/balances
  ({"smartAccountAddress", "balances": [{"smartWalletId", "currency",
  "balance", "error"}]}).
- Transfers (Prompt 13): POST /v1/users/{userId}/withdrawal/wallet/nigeria
  (bank payout, body {sourceSmartWalletId, bankAccountId, fromAmount}) or
  .../withdrawal/smart-wallet/crypto (on-chain payout, body
  {sourceSmartWalletId, destinationChain, destinationCurrency,
  destinationAddress, amount}) each return {proposalId, signPayload} in one
  call (or {signPayloadPending: true} if the upstream hasn't prepared it
  synchronously -- no documented polling endpoint exists yet for that case,
  so it surfaces as a loud BMONITransferError here rather than a silent
  retry loop). `signPayload` is a wrapper -- {signingPayloadHash, typedData,
  signatureExpiresAt, proposalStatus} -- confirmed live 2026-07-30. Despite
  `typedData` looking like an EIP-712 struct to sign, the sandbox actually
  verifies a **raw ECDSA signature over `signingPayloadHash` directly**
  (`Account.unsafe_sign_hash`), not a `sign_typed_data` signature over
  `typedData`: signing `typedData` (or the original bug, passing the whole
  `signPayload` wrapper) both get a live 400 `{"code":"E101","message":
  "Signature does not match your registered owner address"}` from
  POST .../sign, even though the recovered address is the correct owner --
  the sandbox is doing a plain ecrecover against `signingPayloadHash`, and
  `typedData` is present only for wallet-UI display, not what's actually
  verified. Confirmed by direct experiment against a live proposal: the
  EIP-712-signed variant 400s, the raw-hash-signed variant 200s with
  `currentSignatures: 1`. Then POST
  /v1/users/{userId}/smart-wallets/proposals/{proposalId}/sign with
  {signature}. The signature must be a 65-byte 0x-prefixed hex string --
  eth_account's HexBytes.hex() in the pinned dependency versions does *not*
  include the "0x" prefix, so callers must prepend it themselves (confirmed
  live: the sandbox 400s on a signature missing it). BMONI's KMS
  co-signature is appended automatically server-side -- nothing further is
  needed from us.
- A Nigerian withdrawal destination must already be a registered withdrawal
  bank account (POST /v1/users/{userId}/bank-accounts/withdrawal-accounts/
  nigeria, after verifying it via .../verify-nigerian-account) before
  /withdrawal/wallet/nigeria will accept its id as bankAccountId; that
  registration is demo/onboarding setup, not something this client does
  per-transfer.
- No documented endpoints exist for a social graph, a decision-log
  write-back, or a transfer-intent pre-authorization hook. Those methods are
  therefore deliberate no-ops here (not network calls that would always
  404/fail) so the rest of the pipeline degrades the same way it already does
  for a stub with no social graph.

Every real response is still logged at DEBUG so future schema drift can be
diagnosed against a live sandbox call.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

import httpx
from eth_account import Account
from eth_account.signers.local import LocalAccount

from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import BMONI_API_KEY, BMONI_BASE_URL
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

    TODO(bmoni-schema): field names below are still a best guess -- confirmed
    live only that GET .../{smartWalletId}/transactions returns
    {"transactions": [...]} (see module docstring); the sandbox accounts
    used to confirm the read path had an empty transaction list at the time
    this was last checked (freshly onboarded, unfunded demo identities), so
    the shape of an individual record is unconfirmed. Defaulting to
    decimal-naira amounts (e.g. "1000.00"), matching how amounts are quoted
    everywhere else in the sandbox's own OpenAPI spec (GET /docs/openapi.json),
    not kobo-style integers or raw 18-decimal token units.
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

        resolved_key = api_key if api_key is not None else BMONI_API_KEY
        if not resolved_key:
            raise ValueError(
                "BMONI_API_KEY is required to construct a real BMONIClient "
                "(set it in the environment or pass api_key explicitly)"
            )

        self._client = httpx.AsyncClient(
            base_url=base_url or BMONI_BASE_URL,
            headers={"x-api-key": resolved_key, "Content-Type": "application/json"},
        )

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        """Transactions across every smart wallet (currency) this user has.

        There is no user-wide transactions endpoint -- only
        GET .../smart-wallets/{smartWalletId}/transactions, scoped to one
        currency's wallet. This fans out over every wallet balances()
        reports for the user and concatenates the results.
        """
        try:
            balance_response = await self._client.get(
                f"/v1/users/{user_id}/smart-wallets/account/balances"
            )
            balance_response.raise_for_status()
            balances_payload = balance_response.json()
            wallet_ids = [
                entry["smartWalletId"]
                for entry in balances_payload.get("balances", [])
                if isinstance(entry, dict) and "smartWalletId" in entry
            ]
        except (httpx.HTTPError, TypeError, ValueError, KeyError):
            logger.warning(
                "BMONI get_transaction_history failed to list wallets for user_id=%s",
                user_id,
                exc_info=True,
            )
            return []

        transactions: list[Transaction] = []
        for wallet_id in wallet_ids:
            try:
                response = await self._client.get(
                    f"/v1/users/{user_id}/smart-wallets/{wallet_id}/transactions"
                )
                response.raise_for_status()
                payload = response.json()
                logger.debug(
                    "BMONI raw transaction history response for user_id=%s wallet_id=%s: %r",
                    user_id,
                    wallet_id,
                    payload,
                )
                records = payload.get("transactions", []) if isinstance(payload, dict) else payload
                parsed = (_parse_transaction(record) for record in records)
                transactions.extend(t for t in parsed if t is not None)
            except (httpx.HTTPError, TypeError, ValueError):
                logger.warning(
                    "BMONI get_transaction_history failed for user_id=%s wallet_id=%s",
                    user_id,
                    wallet_id,
                    exc_info=True,
                )
        return transactions

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

        `destination` must carry `sourceSmartWalletId` (the wallet the funds
        leave from) plus, per rail:
          - "nigeria": `bankAccountId` -- an id already returned by POST
            .../bank-accounts/withdrawal-accounts/nigeria (that registration
            is demo/onboarding setup, done once per identity, not here).
          - "crypto": `destinationChain`, `destinationCurrency`,
            `destinationAddress`.
        The amount field the real API expects ("fromAmount" for nigeria,
        "amount" for crypto) is always computed from `amount_kobo`, never
        taken from `destination`: `destination` is caller-supplied and must
        never be able to change what amount BMONI actually moves after
        Sentri has scored `amount_kobo` -- that would let a transfer bypass
        scoring entirely.

        `signer` is the demo identity's server-held keypair (see
        sentri.bmoni.signing) -- the same one that owns the smart wallet,
        since the owner address is fixed at wallet-creation time.
        """
        decimal_amount = f"{amount_kobo / 100:.2f}"
        if destination_type == "nigeria":
            proposal_path = f"/v1/users/{user_id}/withdrawal/wallet/nigeria"
            body = {
                "sourceSmartWalletId": destination["sourceSmartWalletId"],
                "bankAccountId": destination["bankAccountId"],
                "fromAmount": decimal_amount,
            }
        else:
            proposal_path = f"/v1/users/{user_id}/withdrawal/smart-wallet/crypto"
            body = {
                "sourceSmartWalletId": destination["sourceSmartWalletId"],
                "destinationChain": destination["destinationChain"],
                "destinationCurrency": destination["destinationCurrency"],
                "destinationAddress": destination["destinationAddress"],
                "amount": decimal_amount,
            }

        try:
            proposal_response = await self._client.post(proposal_path, json=body)
            proposal_response.raise_for_status()
        except httpx.HTTPError as exc:
            raise BMONITransferError(f"withdrawal proposal request failed: {exc}") from exc

        proposal = proposal_response.json()
        logger.debug("BMONI raw withdrawal-proposal response for user_id=%s: %r", user_id, proposal)

        if proposal.get("signPayloadPending"):
            raise BMONITransferError(
                "withdrawal proposal's sign payload was not ready synchronously "
                f"(signPayloadHint={proposal.get('signPayloadHint')!r}); no polling "
                f"endpoint is implemented for this case yet: {proposal!r}"
            )

        try:
            proposal_id = proposal["proposalId"]
            signing_payload_hash = proposal["signPayload"]["signingPayloadHash"]
        except KeyError as exc:
            raise BMONITransferError(
                f"withdrawal proposal response missing {exc}: {proposal!r}"
            ) from exc

        signed = Account.unsafe_sign_hash(signing_payload_hash, signer.key)

        try:
            sign_response = await self._client.post(
                f"/v1/users/{user_id}/smart-wallets/proposals/{proposal_id}/sign",
                json={"signature": "0x" + signed.signature.hex()},
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
