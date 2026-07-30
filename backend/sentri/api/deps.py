"""Dependency-injection factories for the API layer.

Kept in their own module (rather than inline in main.py) so that route
modules can import them without a circular import against the app factory,
which in turn imports the route modules to wire them onto the app.

BMONI_API_KEY, ANTHROPIC_API_KEY, and SENTRI_SEED_PATH are read here via
os.environ.get() at call time, deliberately not through sentri.config (whose
constants are frozen at that module's own import time, which happens well
before these factories are ever called). Each factory is still only
evaluated once thanks to @lru_cache, so this isn't about re-reading the
environment on every request -- it's about not freezing the read before
tests (or any other post-import env mutation) get a chance to set it. Tried
routing these through sentri.config once; tests/test_deps.py is what caught
it silently breaking monkeypatch-based overrides.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import anthropic

from sentri.bmoni.client import BMONIClient as RealBMONIClient
from sentri.bmoni.protocol import BMONIClient
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.synthesizer.claude import ClaudeSynthesizer
from sentri.synthesizer.protocol import ExplanationSynthesizer
from sentri.synthesizer.template import template_explanation


class TemplateOnlySynthesizer:
    """Fallback synthesizer used when no Anthropic API key is configured.

    Always renders through the deterministic template path.
    """

    async def synthesize(
        self,
        deviation: DeviationVector,
        facts: dict[str, Any],
        triggered: list[TriggerReason],
        language: str,
    ) -> tuple[str, str]:
        return template_explanation(triggered, facts, language), "template"


@lru_cache(maxsize=1)
def get_bmoni_client() -> BMONIClient:
    """Dependency factory for the BMONI adapter.

    Uses the real sandbox-backed RealBMONIClient when BMONI_API_KEY is set;
    otherwise falls back to the in-memory stub, same pattern as get_synthesizer.
    """
    api_key = os.environ.get("BMONI_API_KEY")
    if api_key:
        return RealBMONIClient(api_key=api_key)
    seed_path = os.environ.get("SENTRI_SEED_PATH")
    return InMemoryBMONIStub(seed_path=seed_path)


@lru_cache(maxsize=1)
def get_synthetic_bmoni_client() -> InMemoryBMONIStub:
    """Always the in-memory synthetic stub, regardless of BMONI_API_KEY.

    Lets /transfer score a bridged demo user's pending transfer against their
    synthetic historical baseline (Prompt 12) even when get_bmoni_client()
    resolves to the real sandbox client for actually executing the live
    withdrawal (Prompt 13).
    """
    seed_path = os.environ.get("SENTRI_SEED_PATH")
    return InMemoryBMONIStub(seed_path=seed_path)


@lru_cache(maxsize=1)
def get_synthesizer() -> ExplanationSynthesizer:
    """Dependency factory for the Tier 2 synthesizer.

    Uses ClaudeSynthesizer when ANTHROPIC_API_KEY is set; otherwise falls back
    to a synthesizer that always renders the deterministic template.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return ClaudeSynthesizer(anthropic.Anthropic(api_key=api_key))
    return TemplateOnlySynthesizer()
