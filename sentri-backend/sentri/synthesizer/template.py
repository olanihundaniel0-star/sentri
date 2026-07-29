"""Deterministic, guaranteed-safe template fallback for explanations."""

from __future__ import annotations

from typing import Any, Callable

from sentri.models.deviation import TriggerReason

_TEMPLATES: dict[TriggerReason, tuple[tuple[str, ...], Callable[[dict[str, Any]], str]]] = {
    TriggerReason.RECIPIENT_FAMILIARITY: (
        (),
        lambda f: "You've never sent money to this account.",
    ),
    TriggerReason.GRAPH_PROXIMITY: (
        (),
        lambda f: "This account has no connection to anyone you've sent money to before.",
    ),
    TriggerReason.AMOUNT_Z_RECIPIENT: (
        ("min_amount_display", "max_amount_display", "amount_display"),
        lambda f: (
            f"You usually send between {f['min_amount_display']} and {f['max_amount_display']} "
            f"to this recipient. This is {f['amount_display']}."
        ),
    ),
    TriggerReason.AMOUNT_Z_GLOBAL: (
        ("min_amount_display", "max_amount_display", "amount_display"),
        lambda f: (
            f"You usually send between {f['min_amount_display']} and {f['max_amount_display']} "
            f"to new recipients. This is {f['amount_display']}."
        ),
    ),
    TriggerReason.AMOUNT_DRIFT: (
        ("prior_mean_display", "recent_mean_display"),
        lambda f: (
            f"Your recent transfers to this recipient have grown from around "
            f"{f['prior_mean_display']} to {f['recent_mean_display']}."
        ),
    ),
    TriggerReason.HOUR_DEVIATION: (
        ("time_of_day", "typical_hours"),
        lambda f: f"This is at {f['time_of_day']}. You usually send money between {f['typical_hours']}.",
    ),
    TriggerReason.CURRENCY_NOVELTY: (
        ("currency",),
        lambda f: f"This is your first transfer in {f['currency']}.",
    ),
    TriggerReason.CROSS_BORDER: (
        (),
        lambda f: "This transfer is crossing borders.",
    ),
}


def template_explanation(
    triggered: list[TriggerReason], facts: dict[str, Any], language: str = "en"
) -> str:
    """Render a canned, factual sentence per triggered reason. Skips reasons missing required facts."""
    sentences: list[str] = []
    for reason in triggered:
        entry = _TEMPLATES.get(reason)
        if entry is None:
            continue
        required_keys, render = entry
        if any(key not in facts for key in required_keys):
            continue
        sentences.append(render(facts))
    return " ".join(sentences)
