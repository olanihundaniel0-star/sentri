"""In-memory BMONI stub backed by seeds/data.json, for local dev and tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from sentri.canonical.timestamps import ingest_timestamp
from sentri.models.profile import SocialGraph
from sentri.models.transaction import Transaction

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
# sentri/bmoni/stub.py → sentri/bmoni/ → sentri/ → repo root
_DEFAULT_SEED_PATH = _PROJECT_ROOT / "seeds" / "data.json"


def _parse_transaction(raw: dict[str, Any]) -> Transaction:
    return Transaction(
        amount_kobo=raw["amount_kobo"],
        timestamp=ingest_timestamp(raw["timestamp"]),
        recipient_id=raw["recipient_id"],
        currency=raw.get("currency", "NGN"),
        memo=raw.get("memo"),
    )


class InMemoryBMONIStub:
    """Structurally implements BMONIClient using seed data held in memory."""

    def __init__(self, seed_path: Path | str | None = None) -> None:
        resolved = Path(seed_path) if seed_path else _DEFAULT_SEED_PATH
        raw = json.loads(resolved.read_text(encoding="utf-8"))

        self._friends_by_id: dict[str, list[str]] = {}
        self._has_social_graph: dict[str, bool] = {}
        self._transactions_by_id: dict[str, list[Transaction]] = {}

        for user in raw["users"]:
            user_id = user["user_id"]
            self._friends_by_id[user_id] = user["friends"]
            self._has_social_graph[user_id] = user["has_social_graph"]
            self._transactions_by_id[user_id] = [
                _parse_transaction(txn) for txn in user["transactions"]
            ]

        self.decisions: list[dict[str, Optional[str]]] = []
        self._transfer_intent_callback: Optional[Any] = None

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        return self._transactions_by_id.get(user_id, [])

    async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]:
        if not self._has_social_graph.get(user_id, False):
            return None

        friends = self._friends_by_id.get(user_id, [])
        friends_of_friends = {
            friend_id: frozenset(self._friends_by_id.get(friend_id, [])) for friend_id in friends
        }
        return SocialGraph(
            user_id=user_id,
            friends=frozenset(friends),
            friends_of_friends=friends_of_friends,
        )

    async def log_decision(
        self,
        user_id: str,
        event_id: str,
        decision: str,
        explanation: Optional[str],
    ) -> None:
        self.decisions.append(
            {
                "user_id": user_id,
                "event_id": event_id,
                "decision": decision,
                "explanation": explanation,
            }
        )

    async def on_transfer_intent_hook(self, callback: Any) -> None:
        self._transfer_intent_callback = callback
