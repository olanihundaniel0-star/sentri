"""Claude-backed Tier 2 explanation synthesizer, with a guaranteed-safe fallback."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Optional

import anthropic

from sentri.config import Config
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.synthesizer.prompt import SYSTEM_PROMPT, build_llm_input
from sentri.synthesizer.template import template_explanation
from sentri.synthesizer.validator import validate

logger = logging.getLogger(__name__)


class ClaudeSynthesizer:
    """Synthesizes explanations via the Anthropic API, validating and falling back to templates."""

    def __init__(self, client: anthropic.Anthropic) -> None:
        self._client = client

    async def synthesize(
        self,
        deviation: DeviationVector,
        facts: dict[str, Any],
        triggered: list[TriggerReason],
        language: str,
    ) -> tuple[str, str]:
        payload = build_llm_input(deviation, facts, triggered, language)

        try:
            output = await asyncio.wait_for(
                asyncio.to_thread(self._call_claude, payload),
                timeout=Config.LLM_TIMEOUT_SECONDS,
            )

            if output is None:
                return template_explanation(triggered, facts, language), "template"

            is_valid, _ = validate(output, facts, language)
            if not is_valid:
                return template_explanation(triggered, facts, language), "template"

            return output, "claude"
        except (
            asyncio.TimeoutError,
            anthropic.APITimeoutError,
            anthropic.APIError,
            AttributeError,
            IndexError,
        ):
            return template_explanation(triggered, facts, language), "template"

    def _call_claude(self, payload: dict[str, Any]) -> Optional[str]:
        message = self._client.with_options(timeout=Config.LLM_TIMEOUT_SECONDS).messages.create(
            model=Config.LLM_MODEL,
            max_tokens=Config.LLM_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(payload)}],
        )
        for block in message.content:
            if block.type == "text":
                return block.text

        logger.warning(
            "Claude response had no text block (stop_reason=%s)",
            getattr(message, "stop_reason", None),
        )
        return None
