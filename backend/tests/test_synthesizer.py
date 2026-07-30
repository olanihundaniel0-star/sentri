"""Tests for the Tier 2 synthesizer: validator, template fallback, and Claude wrapper."""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.synthesizer.claude import ClaudeSynthesizer
from sentri.synthesizer.template import template_explanation
from sentri.synthesizer.validator import validate

_VALID_FACTS = {
    "min_amount_kobo": 800000,
    "min_amount_display": "₦8,000",
    "max_amount_kobo": 4500000,
    "max_amount_display": "₦45,000",
    "amount_kobo": 48000000,
    "amount_display": "₦480,000",
    "time_of_day": "2:47am",
}
_VALID_OUTPUT = (
    "You've never sent money to this account. "
    "You usually send between ₦8,000 and ₦45,000 to new recipients. "
    "This is ₦480,000, at 2:47am."
)


def test_validate_rejects_verdict_keyword() -> None:
    is_valid, reason = validate("This looks like fraud", {}, "en")
    assert is_valid is False
    assert reason == "verdict_keyword_present"


def test_validate_rejects_advice_keyword() -> None:
    is_valid, reason = validate("Be careful — this account is new", {}, "en")
    assert is_valid is False
    assert reason == "verdict_keyword_present"


def test_validate_rejects_unsupported_number() -> None:
    is_valid, reason = validate("The amount is 999999999", {"amount_kobo": 1000}, "en")
    assert is_valid is False
    assert reason.startswith("unsupported_numeric:")


def test_validate_accepts_grounded_output() -> None:
    is_valid, reason = validate(_VALID_OUTPUT, _VALID_FACTS, "en")
    assert is_valid is True
    assert reason == ""


def test_validate_rejects_when_fact_removed() -> None:
    facts = dict(_VALID_FACTS)
    del facts["amount_kobo"]
    is_valid, reason = validate(_VALID_OUTPUT, facts, "en")
    assert is_valid is False
    assert reason.startswith("unsupported_numeric:")


def test_validate_accepts_decimal_kobo_display() -> None:
    facts = {"amount_kobo": 45012375, "amount_display": "₦450,123.75"}
    is_valid, reason = validate("This is ₦450,123.75.", facts, "en")
    assert is_valid is True
    assert reason == ""


def test_validate_rejects_rounded_decimal_kobo_display() -> None:
    facts = {"amount_kobo": 45012375, "amount_display": "₦450,123.75"}
    is_valid, reason = validate("This is ₦450,124.", facts, "en")
    assert is_valid is False
    assert reason.startswith("unsupported_numeric:")


@pytest.mark.parametrize(
    "output",
    ["This is ₦450,000.", "This is ₦450,000.00.", "This is 450000."],
)
def test_validate_accepts_equivalent_whole_naira_outputs(output: str) -> None:
    facts = {"amount_kobo": 45000000, "amount_display": "₦450,000"}
    is_valid, reason = validate(output, facts, "en")
    assert is_valid is True
    assert reason == ""


def test_validate_rejects_too_long() -> None:
    output = "One. Two. Three. Four."
    is_valid, reason = validate(output, {}, "en")
    assert is_valid is False
    assert reason == "too_long"


_ALL_FACTS = {
    "min_amount_kobo": 800000,
    "min_amount_display": "₦8,000",
    "max_amount_kobo": 4500000,
    "max_amount_display": "₦45,000",
    "amount_kobo": 48000000,
    "amount_display": "₦480,000",
    "prior_mean_kobo": 1000000,
    "prior_mean_display": "₦10,000",
    "recent_mean_kobo": 9000000,
    "recent_mean_display": "₦90,000",
    "prior_std_kobo": 100000,
    "prior_std_display": "₦1,000",
    "recent_std_kobo": 300000,
    "recent_std_display": "₦3,000",
    "drift_ratio": 3.0,
    "time_of_day": "11:00pm",
    "typical_hours": "9am and 6pm",
    "currency": "USD",
}


@pytest.mark.parametrize("reason", list(TriggerReason))
def test_template_explanation_non_empty_with_adequate_facts(reason: TriggerReason) -> None:
    result = template_explanation([reason], _ALL_FACTS, "en")
    assert result != ""


def test_template_explanation_skips_sentence_with_missing_fact() -> None:
    result = template_explanation([TriggerReason.AMOUNT_Z_RECIPIENT], {}, "en")
    assert result == ""
    assert "{" not in result


def _make_deviation() -> DeviationVector:
    return DeviationVector(
        recipient_familiarity=0.0,
        graph_proximity=None,
        amount_z_recipient=None,
        amount_z_global=5.0,
        amount_drift_ratio=None,
        hour_deviation=0.1,
        currency_novelty=False,
        cross_border=False,
        z_score_path="global_z_min_samples",
    )


async def test_claude_synthesizer_falls_back_to_template_on_invalid_output() -> None:
    fake_message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="This looks like fraud")]
    )
    mock_client = MagicMock()
    mock_client.with_options.return_value.messages.create.return_value = fake_message

    synthesizer = ClaudeSynthesizer(mock_client)
    deviation = _make_deviation()
    triggered = [TriggerReason.RECIPIENT_FAMILIARITY]

    text, used = await synthesizer.synthesize(deviation, {}, triggered, "en")

    assert used == "template"
    assert text == template_explanation(triggered, {}, "en")
    mock_client.with_options.return_value.messages.create.assert_called_once()


_FAKE_REQUEST = httpx.Request("POST", "https://api.anthropic.com/v1/messages")


async def test_claude_synthesizer_falls_back_immediately_on_empty_content() -> None:
    fake_message = SimpleNamespace(content=[], stop_reason="refusal")
    mock_client = MagicMock()
    mock_client.with_options.return_value.messages.create.return_value = fake_message

    synthesizer = ClaudeSynthesizer(mock_client)
    deviation = _make_deviation()
    triggered = [TriggerReason.RECIPIENT_FAMILIARITY]

    start = time.perf_counter()
    text, used = await synthesizer.synthesize(deviation, {}, triggered, "en")
    elapsed = time.perf_counter() - start

    assert used == "template"
    assert text == template_explanation(triggered, {}, "en")
    assert elapsed < 0.1


async def test_claude_synthesizer_falls_back_immediately_on_non_text_content() -> None:
    fake_message = SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", input={})],
        stop_reason="tool_use",
    )
    mock_client = MagicMock()
    mock_client.with_options.return_value.messages.create.return_value = fake_message

    synthesizer = ClaudeSynthesizer(mock_client)
    deviation = _make_deviation()
    triggered = [TriggerReason.RECIPIENT_FAMILIARITY]

    start = time.perf_counter()
    text, used = await synthesizer.synthesize(deviation, {}, triggered, "en")
    elapsed = time.perf_counter() - start

    assert used == "template"
    assert text == template_explanation(triggered, {}, "en")
    assert elapsed < 0.1


async def test_claude_synthesizer_falls_back_on_api_timeout_error() -> None:
    mock_client = MagicMock()
    mock_client.with_options.return_value.messages.create.side_effect = anthropic.APITimeoutError(
        request=_FAKE_REQUEST
    )

    synthesizer = ClaudeSynthesizer(mock_client)
    deviation = _make_deviation()
    triggered = [TriggerReason.RECIPIENT_FAMILIARITY]

    text, used = await synthesizer.synthesize(deviation, {}, triggered, "en")

    assert used == "template"
    assert text == template_explanation(triggered, {}, "en")


async def test_claude_synthesizer_falls_back_on_api_error() -> None:
    mock_client = MagicMock()
    mock_client.with_options.return_value.messages.create.side_effect = anthropic.APIError(
        "boom", request=_FAKE_REQUEST, body=None
    )

    synthesizer = ClaudeSynthesizer(mock_client)
    deviation = _make_deviation()
    triggered = [TriggerReason.RECIPIENT_FAMILIARITY]

    text, used = await synthesizer.synthesize(deviation, {}, triggered, "en")

    assert used == "template"
    assert text == template_explanation(triggered, {}, "en")
