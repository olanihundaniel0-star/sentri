"""Real BMONI adapter, calling the embedded-dev sandbox over HTTP.

Ground truth (BMONI Hackathon Quick Start, restated 2026-07-29) that this
module relies on:

- Base URL is https://embedded-dev.bmoni.com; every documented path already
  starts with /v1, so this client never adds another /v1 prefix.
- Auth on every request: header x-api-key: <BMONI_API_KEY>, plus
  Content-Type: application/json.
- Reads: GET /v1/users/{userId}/smart-wallets/account/transactions and
  .../account/balances.
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
from typing import Any, Optional

import httpx

from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import Config
from sentri.models.profile import SocialGraph
from sentri.models.transaction import Transaction

logger = logging.getLogger(__name__)


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

    async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]:
        """No social-graph endpoint is documented; graph_proximity keeps its
        existing 0.0 fallback, same as for any user with no graph."""
        return None

    async def log_decision(
        self,
        user_id: str,
        event_id: str,
        decision: str,
        explanation: Optional[str],
    ) -> None:
        """No decision-log write-back endpoint is documented; deliberate no-op."""
        return None

    async def on_transfer_intent_hook(self, callback: Any) -> None:
        """No transfer-intent pre-authorization hook is documented yet."""
        return None

    async def aclose(self) -> None:
        await self._client.aclose()
