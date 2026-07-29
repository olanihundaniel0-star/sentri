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

    async def log_decision(
        self,
        user_id: str,
        event_id: str,
        decision: str,
        explanation: Optional[str],
    ) -> None:
        """Record a Sentri verdict back to BMONI for audit/feedback purposes."""
        ...

    async def on_transfer_intent_hook(self, callback: Any) -> None:
        """Register a pre-authorization callback. Signature TBD pending BMONI's contract."""
        ...
