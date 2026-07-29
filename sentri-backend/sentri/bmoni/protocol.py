"""BMONI adapter interface. Sentri talks to BMONI only through this Protocol."""

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

from sentri.models.profile import SocialGraph
from sentri.models.transaction import Transaction


@runtime_checkable
class BMONIClient(Protocol):
    """Interface a BMONI adapter (real or stub) must satisfy."""

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        """Return a user's historical transactions, oldest and newest in any order."""
        ...

    async def get_social_graph(self, user_id: str) -> Optional[SocialGraph]:
        """Return the user's social graph, or None when BMONI does not expose one."""
        ...

    async def on_transfer_intent_hook(self, callback: Any) -> None:
        """Register a pre-authorization callback. Signature TBD pending BMONI's contract."""
        ...
