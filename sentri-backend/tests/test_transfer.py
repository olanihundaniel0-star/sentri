"""Tests for POST /transfer and /transfer/{id}/confirm (Prompt 13)."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

import sentri.api.transfer as transfer_module
from sentri.api.deps import TemplateOnlySynthesizer
from sentri.api.transfer import confirm_transfer, create_transfer
from sentri.bmoni.client import BMONITransferError
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.canonical.timestamps import ingest_timestamp
from sentri.models.transfer import TransferRequest, TransferStatus
from seeds.generator import generate_seed_data, write_seed_data


@pytest.fixture(scope="module")
def cohort_test_cases() -> dict[str, dict[str, Any]]:
    write_seed_data()
    data = generate_seed_data()
    by_cohort: dict[str, dict[str, Any]] = {}
    for test_case in data["test_cases"]:
        by_cohort.setdefault(test_case["cohort"], test_case)
    return by_cohort


def _transfer_request(test_case: dict[str, Any]) -> TransferRequest:
    event = test_case["event"]
    return TransferRequest(
        user_id=event["user_id"],
        amount_kobo=event["amount_kobo"],
        recipient_id=event["recipient_id"],
        currency=event.get("currency", "NGN"),
        destination={"accountNumber": "0001112222", "bankCode": "044"},
    )


@pytest.fixture(autouse=True)
def _clear_pending_transfers() -> Any:
    transfer_module._pending_transfers.clear()
    yield
    transfer_module._pending_transfers.clear()


class _FakeRealClient:
    """Stand-in for sentri.bmoni.client.BMONIClient, patched in as RealBMONIClient."""

    def __init__(self) -> None:
        self.transfer_calls: list[dict[str, Any]] = []

    async def transfer(
        self,
        user_id: str,
        signer: Any,
        amount_kobo: int,
        destination: dict[str, Any],
        destination_type: str = "nigeria",
    ) -> dict[str, Any]:
        self.transfer_calls.append(
            {
                "user_id": user_id,
                "amount_kobo": amount_kobo,
                "destination": destination,
                "destination_type": destination_type,
            }
        )
        return {"proposalId": "prop-1", "status": "submitted"}


class _FailingRealClient:
    """Stand-in for sentri.bmoni.client.BMONIClient whose transfer() always fails."""

    async def transfer(
        self,
        user_id: str,
        signer: Any,
        amount_kobo: int,
        destination: dict[str, Any],
        destination_type: str = "nigeria",
    ) -> dict[str, Any]:
        raise BMONITransferError("sandbox rejected the withdrawal proposal")


def _bridged(real_user_id: str = "bmoni-real-001") -> Any:
    return patch.multiple(
        transfer_module,
        real_bmoni_user_id=MagicMock(return_value=real_user_id),
        signing_account=MagicMock(return_value=MagicMock()),
    )


@contextmanager
def _frozen_at_cohort_time(test_case: dict[str, Any]) -> Iterator[None]:
    """create_transfer scores against datetime.now(), but cohort test cases are
    anchored to seeds/generator.py's fixed _REFERENCE_DATE -- freeze only the
    *first* datetime.now() call (the TransactionEvent's timestamp) to the
    cohort's own designed time, so its intended silent-pass/intervene outcome
    doesn't depend on the wall-clock time the test happens to run at. Later
    calls (a held transfer's created_at bookkeeping) fall through to the real
    clock, since that timestamp is TTL bookkeeping, not scoring input, and
    must reflect genuine wall-clock time for expiry pruning to behave sanely.
    """
    frozen = ingest_timestamp(test_case["event"]["timestamp"])
    real_now = datetime.now
    call_count = [0]

    def _now(tz: Any = None) -> datetime:
        call_count[0] += 1
        return frozen if call_count[0] == 1 else real_now(tz)

    with patch.object(transfer_module, "datetime") as mock_datetime:
        mock_datetime.now.side_effect = _now
        yield


async def test_create_transfer_rejects_unbridged_user(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["D"])
    request = request.model_copy(update={"user_id": "user_099"})

    with pytest.raises(HTTPException) as exc_info:
        await create_transfer(request, InMemoryBMONIStub(), TemplateOnlySynthesizer())

    assert exc_info.value.status_code == 400


async def test_create_transfer_holds_when_intervene_fires(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["A"])
    fake_client = _FakeRealClient()

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        response = await create_transfer(request, fake_client, TemplateOnlySynthesizer())  # type: ignore[arg-type]

    assert response.status == TransferStatus.HELD
    assert response.transfer_id is not None
    assert response.explanation
    assert response.triggered_reasons
    assert fake_client.transfer_calls == []
    assert transfer_module._pending_transfers[response.transfer_id].request == request


async def test_create_transfer_executes_immediately_on_silent_pass(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["D"])
    fake_client = _FakeRealClient()

    with (
        _bridged(),
        _frozen_at_cohort_time(cohort_test_cases["D"]),
        patch.object(transfer_module, "RealBMONIClient", _FakeRealClient),
    ):
        response = await create_transfer(request, fake_client, TemplateOnlySynthesizer())  # type: ignore[arg-type]

    assert response.status == TransferStatus.EXECUTED
    assert response.bmoni_result == {"proposalId": "prop-1", "status": "submitted"}
    assert len(fake_client.transfer_calls) == 1
    assert fake_client.transfer_calls[0]["user_id"] == "bmoni-real-001"
    assert transfer_module._pending_transfers == {}


async def test_create_transfer_503s_when_bmoni_client_is_not_real(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["D"])

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["D"]):
        with pytest.raises(HTTPException) as exc_info:
            await create_transfer(request, InMemoryBMONIStub(), TemplateOnlySynthesizer())

    assert exc_info.value.status_code == 503


async def test_confirm_transfer_executes_pending_and_removes_it(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["A"])
    fake_client = _FakeRealClient()

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        held = await create_transfer(request, fake_client, TemplateOnlySynthesizer())  # type: ignore[arg-type]
    assert held.transfer_id is not None

    with _bridged(), patch.object(transfer_module, "RealBMONIClient", _FakeRealClient):
        response = await confirm_transfer(held.transfer_id, fake_client)  # type: ignore[arg-type]

    assert response.status == TransferStatus.EXECUTED
    assert len(fake_client.transfer_calls) == 1
    assert held.transfer_id not in transfer_module._pending_transfers


async def test_confirm_transfer_404s_for_unknown_id() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await confirm_transfer("does-not-exist", InMemoryBMONIStub())

    assert exc_info.value.status_code == 404


async def test_create_transfer_returns_clean_502_on_bmoni_transfer_error(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["D"])

    with (
        _bridged(),
        _frozen_at_cohort_time(cohort_test_cases["D"]),
        patch.object(transfer_module, "RealBMONIClient", _FailingRealClient),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await create_transfer(request, _FailingRealClient(), TemplateOnlySynthesizer())  # type: ignore[arg-type]

    assert exc_info.value.status_code == 502


async def test_confirm_transfer_returns_clean_502_on_bmoni_transfer_error(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["A"])

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        held = await create_transfer(request, _FailingRealClient(), TemplateOnlySynthesizer())  # type: ignore[arg-type]
    assert held.transfer_id is not None

    with _bridged(), patch.object(transfer_module, "RealBMONIClient", _FailingRealClient):
        with pytest.raises(HTTPException) as exc_info:
            await confirm_transfer(held.transfer_id, _FailingRealClient())  # type: ignore[arg-type]

    assert exc_info.value.status_code == 502
    # A failed confirm means BMONI never confirmed anything moved, so the
    # transfer_id must stay retryable, not be silently lost.
    assert held.transfer_id in transfer_module._pending_transfers


async def test_confirm_transfer_404s_for_expired_pending_transfer(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["A"])

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        held = await create_transfer(request, _FakeRealClient(), TemplateOnlySynthesizer())  # type: ignore[arg-type]
    assert held.transfer_id is not None

    stale = transfer_module._pending_transfers[held.transfer_id]
    transfer_module._pending_transfers[held.transfer_id] = transfer_module._PendingTransfer(
        request=stale.request,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=11),
    )

    with pytest.raises(HTTPException) as exc_info:
        await confirm_transfer(held.transfer_id, InMemoryBMONIStub())

    assert exc_info.value.status_code == 404
    assert held.transfer_id not in transfer_module._pending_transfers


async def test_expired_pending_transfers_are_pruned_on_the_next_write(
    cohort_test_cases: dict[str, dict[str, Any]],
) -> None:
    request = _transfer_request(cohort_test_cases["A"])

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        held = await create_transfer(request, _FakeRealClient(), TemplateOnlySynthesizer())  # type: ignore[arg-type]
    assert held.transfer_id is not None

    stale = transfer_module._pending_transfers[held.transfer_id]
    transfer_module._pending_transfers[held.transfer_id] = transfer_module._PendingTransfer(
        request=stale.request,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=11),
    )

    with _bridged(), _frozen_at_cohort_time(cohort_test_cases["A"]):
        await create_transfer(request, _FakeRealClient(), TemplateOnlySynthesizer())  # type: ignore[arg-type]

    assert held.transfer_id not in transfer_module._pending_transfers
