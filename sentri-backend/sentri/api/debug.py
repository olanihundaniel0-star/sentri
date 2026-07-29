"""Debug endpoints, feature-flagged via config.DEBUG_ENDPOINTS_ENABLED (default on for MVP)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from sentri.api.deps import get_bmoni_client
from sentri.bmoni.protocol import BMONIClient
from sentri.config import DEBUG_ENDPOINTS_ENABLED
from sentri.graph.builder import build_profile
from sentri.models.profile import UserProfile


def _require_debug_enabled() -> None:
    if not DEBUG_ENDPOINTS_ENABLED:
        raise HTTPException(status_code=404, detail="Not Found")


router = APIRouter(dependencies=[Depends(_require_debug_enabled)])


@router.get("/debug/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/debug/profile/{user_id}")
async def get_profile(
    user_id: str, bmoni_client: BMONIClient = Depends(get_bmoni_client)
) -> UserProfile:
    transactions = await bmoni_client.get_transaction_history(user_id)
    social_graph = await bmoni_client.get_social_graph(user_id)
    return build_profile(user_id, transactions, social_graph)
