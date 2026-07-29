"""End-to-end tests for the /evaluate and /debug endpoints."""

from __future__ import annotations

import logging
from math import isclose
from typing import Any, Optional
from unittest.mock import patch

import numpy as np
import pytest

from sentri.api.debug import health
from sentri.api.evaluate import _exclude_current_event, evaluate
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.canonical.timestamps import ingest_timestamp
from sentri.config import THRESHOLDS
from sentri.graph.builder import build_profile
from sentri.models.deviation import DeviationVector, TriggerReason
from sentri.models.profile import UserProfile
from sentri.models.transaction import Transaction, TransactionEvent
from sentri.models.verdict import Verdict, VerdictKind
from sentri.scorer.amount import score_amount
from sentri.scorer.vector import build_vector, fires
from seeds.generator import generate_seed_data, write_seed_data

_DRIFT_KEYS = {
    "recent_std_kobo",
    "recent_std_display",
    "prior_std_kobo",
    "prior_std_display",
    "recent_mean_kobo",
    "recent_mean_display",
    "prior_mean_kobo",
    "prior_mean_display",
    "drift_ratio",
}


class _StubSynthesizer:
    """Predictable synthesizer used in place of Claude so E2E tests never call the API."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def synthesize(
        self,
        deviation: DeviationVector,
        facts: dict[str, Any],
        triggered: list[TriggerReason],
        language: str,
    ) -> tuple[str, str]:
        self.calls.append(
            {
                "deviation": deviation,
                "facts": facts,
                "triggered": triggered,
                "language": language,
            }
        )
        return "This transaction differs from your usual pattern.", "stub"


@pytest.fixture(scope="module")
def cohort_test_cases() -> dict[str, dict[str, Any]]:
    write_seed_data()
    data = generate_seed_data()
    by_cohort: dict[str, dict[str, Any]] = {}
    for test_case in data["test_cases"]:
        by_cohort.setdefault(test_case["cohort"], test_case)
    return by_cohort


def _event_payload(test_case: dict[str, Any]) -> dict[str, Any]:
    return dict(test_case["event"])


def _event(test_case: dict[str, Any]) -> TransactionEvent:
    return TransactionEvent(**_event_payload(test_case))


async def _evaluate_case(
    test_case: dict[str, Any],
) -> tuple[Verdict, _StubSynthesizer]:
    synthesizer = _StubSynthesizer()
    verdict = await evaluate(_event(test_case), InMemoryBMONIStub(), synthesizer)
    return verdict, synthesizer


async def _profile_vector_and_triggered(
    test_case: dict[str, Any],
) -> tuple[TransactionEvent, UserProfile, DeviationVector, list[TriggerReason]]:
    event = _event(test_case)
    stub = InMemoryBMONIStub()
    history = await stub.get_transaction_history(event.user_id)
    social_graph = await stub.get_social_graph(event.user_id)

    event_time = ingest_timestamp(event.timestamp)
    history = _exclude_current_event(history, event, event_time)
    profile = build_profile(event.user_id, history, social_graph)
    vector = build_vector(profile, event, event_time)
    triggered = fires(vector, THRESHOLDS)
    return event, profile, vector, triggered


def _drift_window_amounts(
    profile: UserProfile, event: TransactionEvent
) -> tuple[list[int], list[int]]:
    reference = ingest_timestamp(event.timestamp)
    recent: list[int] = []
    prior: list[int] = []

    for rollup in profile.recipients.values():
        for tx in rollup.transactions:
            age_days = (reference - tx.timestamp).total_seconds() / 86400.0
            if 0 <= age_days <= 30:
                recent.append(tx.amount_kobo)
            elif 30 < age_days <= 90:
                prior.append(tx.amount_kobo)

    return recent, prior


async def test_debug_health() -> None:
    assert await health() == {"status": "ok"}


async def test_cohort_d_is_silent_pass(cohort_test_cases: dict[str, dict[str, Any]]) -> None:
    verdict, synthesizer = await _evaluate_case(cohort_test_cases["D"])
    assert verdict.kind == VerdictKind.SILENT_PASS
    assert verdict.explanation is None
    assert synthesizer.calls == []


async def test_cohort_a_is_intervene_with_explanation(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    verdict, _synthesizer = await _evaluate_case(cohort_test_cases["A"])
    assert verdict.kind == VerdictKind.INTERVENE
    assert verdict.explanation


async def test_cohort_f_excludes_graph_proximity(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    verdict, _synthesizer = await _evaluate_case(cohort_test_cases["F"])
    assert verdict.kind == VerdictKind.INTERVENE
    assert TriggerReason.GRAPH_PROXIMITY not in verdict.triggered_reasons


async def test_evaluate_omits_drift_facts_when_amount_drift_does_not_trigger(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    verdict, synthesizer = await _evaluate_case(cohort_test_cases["A"])

    assert TriggerReason.AMOUNT_DRIFT not in verdict.triggered_reasons
    assert len(synthesizer.calls) == 1
    facts: dict[str, Any] = synthesizer.calls[0]["facts"]
    assert _DRIFT_KEYS.isdisjoint(facts)


async def test_evaluate_includes_scorer_aligned_drift_facts_when_amount_drift_triggers(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    event, profile, _vector, triggered = await _profile_vector_and_triggered(cohort_test_cases["C"])
    amount_score = score_amount(profile, event)

    verdict, synthesizer = await _evaluate_case(cohort_test_cases["C"])

    assert TriggerReason.AMOUNT_DRIFT in triggered
    assert TriggerReason.AMOUNT_DRIFT in verdict.triggered_reasons
    assert len(synthesizer.calls) == 1

    facts: dict[str, Any] = synthesizer.calls[0]["facts"]
    assert _DRIFT_KEYS <= facts.keys()

    recent, prior = _drift_window_amounts(profile, event)
    assert facts["recent_mean_kobo"] == round(sum(recent) / len(recent))
    assert facts["prior_mean_kobo"] == round(sum(prior) / len(prior))
    assert facts["recent_std_kobo"] == int(float(np.std(recent)))
    assert facts["prior_std_kobo"] == int(float(np.std(prior)))
    assert isclose(facts["drift_ratio"], amount_score["amount_drift_ratio"])


async def test_evaluate_logs_intervene_decision(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    stub = InMemoryBMONIStub()
    verdict = await evaluate(_event(cohort_test_cases["A"]), stub, _StubSynthesizer())

    assert verdict.kind == VerdictKind.INTERVENE
    assert len(stub.decisions) == 1
    logged = stub.decisions[0]
    assert logged["decision"] == "INTERVENE"
    assert logged["explanation"] == verdict.explanation
    event_id = logged["event_id"]
    assert isinstance(event_id, str)
    assert len(event_id) == 16
    int(event_id, 16)


async def test_evaluate_logs_silent_pass_decision(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    stub = InMemoryBMONIStub()
    verdict = await evaluate(_event(cohort_test_cases["D"]), stub, _StubSynthesizer())

    assert verdict.kind == VerdictKind.SILENT_PASS
    assert len(stub.decisions) == 1
    logged = stub.decisions[0]
    assert logged["decision"] == "SILENT_PASS"
    assert logged["explanation"] is None


async def test_evaluate_derives_deterministic_event_id(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    test_case = cohort_test_cases["A"]

    stub_one = InMemoryBMONIStub()
    await evaluate(_event(test_case), stub_one, _StubSynthesizer())

    stub_two = InMemoryBMONIStub()
    await evaluate(_event(test_case), stub_two, _StubSynthesizer())

    assert stub_one.decisions[0]["event_id"] == stub_two.decisions[0]["event_id"]


class _FailingLogDecisionStub(InMemoryBMONIStub):
    """Stub whose log_decision always raises, to verify /evaluate stays insulated."""

    async def log_decision(
        self,
        user_id: str,
        event_id: str,
        decision: str,
        explanation: Optional[str],
    ) -> None:
        raise RuntimeError("bmoni down")


async def test_evaluate_survives_log_decision_failure(
    cohort_test_cases: dict[str, dict[str, Any]], caplog: pytest.LogCaptureFixture
) -> None:
    event = _event(cohort_test_cases["A"])
    stub = _FailingLogDecisionStub()

    with caplog.at_level(logging.WARNING, logger="sentri.api.evaluate"):
        verdict = await evaluate(event, stub, _StubSynthesizer())

    assert verdict.kind == VerdictKind.INTERVENE
    assert verdict.explanation

    warnings = [r for r in caplog.records if r.getMessage() == "log_decision failed"]
    assert len(warnings) == 1
    assert warnings[0].__dict__["user_id"] == event.user_id


async def test_evaluate_complete_failure_falls_back_to_silent_pass(
    cohort_test_cases: dict[str, dict[str, Any]], caplog: pytest.LogCaptureFixture
) -> None:
    """Fix 1: evaluate_complete now runs inside the outer try, so a failure
    there (e.g. a broken logging backend) still hits the fail-safe path
    instead of propagating as an unhandled 500."""
    event = _event(cohort_test_cases["A"])

    def _raise_on_evaluate_complete(msg: str, *args: Any, **kwargs: Any) -> None:
        if msg == "evaluate_complete":
            raise RuntimeError("logging backend down")

    with caplog.at_level(logging.ERROR, logger="sentri.api.evaluate"):
        with patch("sentri.api.evaluate.logger.info", side_effect=_raise_on_evaluate_complete):
            verdict = await evaluate(event, InMemoryBMONIStub(), _StubSynthesizer())

    assert verdict.kind == VerdictKind.SILENT_PASS
    assert verdict.synthesizer_used == "none"

    failures = [r for r in caplog.records if r.getMessage() == "evaluate_failed"]
    assert len(failures) == 1


class _RaisingHistoryStub(InMemoryBMONIStub):
    """Stub whose get_transaction_history always raises, to exercise /evaluate's
    top-level failure fallback."""

    async def get_transaction_history(self, user_id: str) -> list[Any]:
        raise ValueError("bmoni history unavailable")


class _RaisingSynthesizer:
    """Synthesizer that always raises, to exercise /evaluate's failure fallback."""

    async def synthesize(
        self,
        deviation: DeviationVector,
        facts: dict[str, Any],
        triggered: list[TriggerReason],
        language: str,
    ) -> tuple[str, str]:
        raise RuntimeError("synthesizer down")


async def test_evaluate_falls_back_to_silent_pass_when_history_lookup_fails(
    cohort_test_cases: dict[str, dict[str, Any]], caplog: pytest.LogCaptureFixture
) -> None:
    event = _event(cohort_test_cases["A"])

    with caplog.at_level(logging.ERROR, logger="sentri.api.evaluate"):
        verdict = await evaluate(event, _RaisingHistoryStub(), _StubSynthesizer())

    assert verdict.kind == VerdictKind.SILENT_PASS
    assert verdict.synthesizer_used == "none"

    failures = [r for r in caplog.records if r.getMessage() == "evaluate_failed"]
    assert len(failures) == 1
    assert failures[0].__dict__["user_id"] == event.user_id
    assert failures[0].__dict__["recipient_id"] == event.recipient_id


async def test_evaluate_falls_back_to_silent_pass_when_synthesizer_fails(
    cohort_test_cases: dict[str, dict[str, Any]], caplog: pytest.LogCaptureFixture
) -> None:
    event = _event(cohort_test_cases["A"])

    with caplog.at_level(logging.ERROR, logger="sentri.api.evaluate"):
        verdict = await evaluate(event, InMemoryBMONIStub(), _RaisingSynthesizer())

    assert verdict.kind == VerdictKind.SILENT_PASS
    assert verdict.synthesizer_used == "none"

    failures = [r for r in caplog.records if r.getMessage() == "evaluate_failed"]
    assert len(failures) == 1
    assert failures[0].__dict__["user_id"] == event.user_id
    assert failures[0].__dict__["recipient_id"] == event.recipient_id


async def test_evaluate_logs_start_and_complete(
    cohort_test_cases: dict[str, dict[str, Any]], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="sentri.api.evaluate"):
        verdict = await evaluate(
            _event(cohort_test_cases["A"]), InMemoryBMONIStub(), _StubSynthesizer()
        )

    assert verdict.kind == VerdictKind.INTERVENE

    start_records = [r for r in caplog.records if r.message == "evaluate_start"]
    assert len(start_records) == 1
    assert "user_id" in start_records[0].__dict__
    assert "recipient_id" in start_records[0].__dict__

    complete_records = [r for r in caplog.records if r.message == "evaluate_complete"]
    assert len(complete_records) == 1
    assert "user_id" in complete_records[0].__dict__
    assert "verdict_kind" in complete_records[0].__dict__
    assert "triggered_reasons" in complete_records[0].__dict__
    assert "synthesizer_used" in complete_records[0].__dict__
    assert "latency_ms" in complete_records[0].__dict__


class _EmptyHistoryStub(InMemoryBMONIStub):
    """Stub that returns empty history for all users."""

    async def get_transaction_history(self, user_id: str) -> list[Transaction]:
        return []


async def test_evaluate_silent_pass_on_empty_history(caplog: pytest.LogCaptureFixture) -> None:
    event = TransactionEvent(
        user_id="new_user",
        amount_kobo=50_000_000,
        timestamp="2026-07-26T10:00:00+01:00",
        recipient_id="anyone",
        currency="NGN",
        cross_border=False,
    )

    with caplog.at_level(logging.INFO, logger="sentri.api.evaluate"):
        verdict = await evaluate(event, _EmptyHistoryStub(), _StubSynthesizer())

    assert verdict.kind == VerdictKind.SILENT_PASS
    assert verdict.synthesizer_used == "none"
    assert verdict.explanation is None

    no_history_records = [r for r in caplog.records if r.message == "evaluate_no_history"]
    assert len(no_history_records) == 1
    assert no_history_records[0].__dict__["user_id"] == "new_user"
    assert no_history_records[0].__dict__["recipient_id"] == "anyone"


async def test_stub_loads_seed_data_regardless_of_cwd(monkeypatch: pytest.MonkeyPatch) -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)
        stub = InMemoryBMONIStub()
        history = await stub.get_transaction_history("user_001")
        assert len(history) > 0
