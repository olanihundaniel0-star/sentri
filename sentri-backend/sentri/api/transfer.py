"""POST /transfer: a real, backend-driven BMONI withdrawal, gated by the same
Tier 1 + Tier 2 evaluation /evaluate uses (Prompt 13).

"Explains, never blocks" stays true for /evaluate itself; the hold introduced
here is a property of /transfer alone, since unlike /evaluate this endpoint
actually moves money. If the scorer's should_intervene() fires, the
withdrawal proposal is never created -- the caller gets the explanation back
and must call /transfer/{id}/confirm to execute it anyway. If it passes
silently, the withdrawal runs immediately end-to-end (propose -> sign ->
submit, see BMONIClient.transfer).

Only bridged demo identities (sentri.bmoni.identity_bridge) can transfer:
this is demo wiring for 2 of the 10 synthetic personas, not a general
money-movement API. Scoring always uses the synthetic seed history
(get_synthetic_bmoni_client), never whichever client get_bmoni_client()
resolves to, so a bridged user's baseline stays the already-validated
synthetic data regardless of whether BMONI_API_KEY is set.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from eth_account.signers.local import LocalAccount
from fastapi import APIRouter, Depends, HTTPException

from sentri.api.deps import get_bmoni_client, get_synthesizer, get_synthetic_bmoni_client
from sentri.api.evaluate import evaluate
from sentri.bmoni.client import BMONIClient as RealBMONIClient
from sentri.bmoni.client import BMONITransferError
from sentri.bmoni.identity_bridge import real_bmoni_user_id
from sentri.bmoni.protocol import BMONIClient
from sentri.bmoni.signing import signing_account
from sentri.models.transaction import TransactionEvent
from sentri.models.transfer import TransferRequest, TransferResponse, TransferStatus
from sentri.models.verdict import VerdictKind
from sentri.synthesizer.protocol import ExplanationSynthesizer

router = APIRouter()
logger = logging.getLogger(__name__)

_PENDING_TRANSFER_TTL = timedelta(minutes=10)


@dataclass(frozen=True)
class _PendingTransfer:
    request: TransferRequest
    created_at: datetime


_pending_transfers: dict[str, _PendingTransfer] = {}


def _prune_expired_transfers() -> None:
    now = datetime.now(timezone.utc)
    expired = [
        transfer_id
        for transfer_id, pending in _pending_transfers.items()
        if now - pending.created_at > _PENDING_TRANSFER_TTL
    ]
    for transfer_id in expired:
        del _pending_transfers[transfer_id]


@dataclass(frozen=True)
class _BridgedIdentity:
    real_user_id: str
    signer: LocalAccount


def _require_bridged_identity(seed_user_id: str) -> _BridgedIdentity:
    real_user_id = real_bmoni_user_id(seed_user_id)
    signer = signing_account(seed_user_id)
    if real_user_id is None or signer is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{seed_user_id} is not a bridged demo identity with a server-held "
                "signing key (see sentri.bmoni.identity_bridge and sentri.bmoni.signing)"
            ),
        )
    return _BridgedIdentity(real_user_id=real_user_id, signer=signer)


async def _execute(
    request: TransferRequest, identity: _BridgedIdentity, bmoni_client: BMONIClient
) -> dict[str, Any]:
    if not isinstance(bmoni_client, RealBMONIClient):
        raise HTTPException(
            status_code=503,
            detail="BMONI_API_KEY not configured; live transfers are unavailable",
        )
    try:
        return await bmoni_client.transfer(
            user_id=identity.real_user_id,
            signer=identity.signer,
            amount_kobo=request.amount_kobo,
            destination=request.destination,
            destination_type=request.destination_type,
        )
    except BMONITransferError:
        logger.error(
            "BMONI transfer failed",
            exc_info=True,
            extra={"user_id": request.user_id},
        )
        raise HTTPException(
            status_code=502,
            detail="BMONI rejected or failed to process the transfer",
        ) from None


@router.post("/transfer", response_model=TransferResponse)
async def create_transfer(
    request: TransferRequest,
    bmoni_client: BMONIClient = Depends(get_bmoni_client),
    synthesizer: ExplanationSynthesizer = Depends(get_synthesizer),
) -> TransferResponse:
    identity = _require_bridged_identity(request.user_id)

    event = TransactionEvent(
        user_id=request.user_id,
        amount_kobo=request.amount_kobo,
        timestamp=datetime.now(timezone.utc).isoformat(),
        recipient_id=request.recipient_id,
        currency=request.currency,
        memo=request.memo,
        cross_border=request.cross_border,
        language=request.language,
    )
    verdict = await evaluate(event, get_synthetic_bmoni_client(), synthesizer)

    if verdict.kind == VerdictKind.INTERVENE:
        _prune_expired_transfers()
        transfer_id = uuid.uuid4().hex
        _pending_transfers[transfer_id] = _PendingTransfer(
            request=request, created_at=datetime.now(timezone.utc)
        )
        return TransferResponse(
            status=TransferStatus.HELD,
            transfer_id=transfer_id,
            kind=verdict.kind,
            explanation=verdict.explanation,
            triggered_reasons=verdict.triggered_reasons,
        )

    result = await _execute(request, identity, bmoni_client)
    return TransferResponse(
        status=TransferStatus.EXECUTED,
        kind=verdict.kind,
        explanation=verdict.explanation,
        triggered_reasons=verdict.triggered_reasons,
        bmoni_result=result,
    )


@router.post("/transfer/{transfer_id}/confirm", response_model=TransferResponse)
async def confirm_transfer(
    transfer_id: str,
    bmoni_client: BMONIClient = Depends(get_bmoni_client),
) -> TransferResponse:
    _prune_expired_transfers()
    pending = _pending_transfers.pop(transfer_id, None)
    if pending is None:
        raise HTTPException(
            status_code=404,
            detail="no held transfer with that id (already confirmed, expired, or never existed)",
        )

    identity = _require_bridged_identity(pending.request.user_id)
    try:
        result = await _execute(pending.request, identity, bmoni_client)
    except HTTPException:
        # _execute failed before BMONI confirmed anything moved (see its
        # docstring: BMONITransferError -> 502, never a swallowed failure).
        # Restore the pending transfer so the caller can retry confirm
        # instead of the transfer_id being silently, permanently lost.
        _pending_transfers[transfer_id] = pending
        raise
    return TransferResponse(status=TransferStatus.EXECUTED, bmoni_result=result)
