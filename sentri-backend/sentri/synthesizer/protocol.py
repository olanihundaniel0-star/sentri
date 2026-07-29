"""Tier 2 explanation synthesizer interface."""

from __future__ import annotations

from typing import Any, Protocol

from sentri.models.deviation import DeviationVector, TriggerReason


class ExplanationSynthesizer(Protocol):
    """Turns a deviation vector into a user-facing explanation."""

    async def synthesize(
        self,
        deviation: DeviationVector,
        facts: dict[str, Any],
        triggered: list[TriggerReason],
        language: str,
    ) -> tuple[str, str]:
        """Return (explanation_text, synthesizer_used), where synthesizer_used is "claude" or "template"."""
        ...
