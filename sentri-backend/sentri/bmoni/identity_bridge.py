"""Bridge between the 10 synthetic seed personas and real BMONI sandbox identities.

Exactly 2 of the 10 personas are bridged, per Prompt 12: enough to demo both
/evaluate branches live. user_001 carries cohort A, the cohort already
validated as a live intervene case (see tests/test_e2e.py's
cohort_test_cases["A"] and test_cohort_a_is_intervene_with_explanation).
user_002 carries cohort D, an ordinary/non-anomalous pattern for the
silent-pass branch. See seeds/identity_bridge.json.

Sourcing the transaction under evaluation live from BMONI does not require
touching sentri.api.evaluate: `TransactionEvent` is already the /evaluate
request body, parsed straight from the caller's payload -- it was never
derived from bmoni_client internally. fetch_live_event_for_bridged_user below
builds exactly that payload from a real live transaction. Submitting it to
/evaluate with user_id set to the bridged seed_user_id (e.g. "user_001")
leaves the historical-baseline lookup (bmoni_client.get_transaction_history
in evaluate()) untouched: it keeps resolving against the synthetic seed data
in seeds/data.json for that user_id, exactly as it does for the other 8
personas.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from sentri.bmoni.protocol import BMONIClient
from sentri.models.transaction import TransactionEvent

logger = logging.getLogger(__name__)

_DEFAULT_BRIDGE_PATH = Path(__file__).resolve().parents[2] / "seeds" / "identity_bridge.json"
_PLACEHOLDER_PREFIX = "REPLACE_"


def _load_bridge(bridge_path: Path | str | None = None) -> dict[str, dict[str, str]]:
    resolved = Path(bridge_path) if bridge_path else _DEFAULT_BRIDGE_PATH
    if not resolved.is_file():
        return {}
    raw: dict[str, dict[str, str]] = json.loads(resolved.read_text(encoding="utf-8"))
    return raw


def real_bmoni_user_id(seed_user_id: str, bridge_path: Path | str | None = None) -> Optional[str]:
    """Real bmoniUserId bridged to a synthetic seed user.

    Returns None when the user isn't bridged at all, or when
    seeds/identity_bridge.json still holds its REPLACE_-prefixed placeholder
    (i.e. scripts/bmoni_onboard.py hasn't been run for this identity yet).
    """
    entry = _load_bridge(bridge_path).get(seed_user_id)
    if entry is None:
        return None
    bmoni_user_id = entry.get("bmoni_user_id", "")
    if not bmoni_user_id or bmoni_user_id.startswith(_PLACEHOLDER_PREFIX):
        return None
    return bmoni_user_id


async def fetch_live_event_for_bridged_user(
    seed_user_id: str,
    real_client: BMONIClient,
    bridge_path: Path | str | None = None,
) -> Optional[TransactionEvent]:
    """Fetch a bridged demo user's most recent live BMONI transaction.

    Returns it packaged as the TransactionEvent /evaluate expects, addressed
    back to the synthetic seed_user_id. Returns None when the user isn't
    bridged (see real_bmoni_user_id) or has no live transaction history yet.

    real_client should be a real sentri.bmoni.client.BMONIClient hitting the
    sandbox -- this function never constructs one itself, matching
    get_bmoni_client as the app's single construction site. The caller then
    submits the returned event to /evaluate through the app's normal
    (typically stub-backed) bmoni_client, so the historical baseline for
    seed_user_id is untouched.
    """
    bmoni_user_id = real_bmoni_user_id(seed_user_id, bridge_path)
    if bmoni_user_id is None:
        return None

    history = await real_client.get_transaction_history(bmoni_user_id)
    if not history:
        return None

    latest = max(history, key=lambda tx: tx.timestamp)
    return TransactionEvent(
        user_id=seed_user_id,
        amount_kobo=latest.amount_kobo,
        timestamp=latest.timestamp.isoformat(),
        recipient_id=latest.recipient_id,
        currency=latest.currency,
        memo=latest.memo,
        cross_border=False,
    )
