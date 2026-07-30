"""Server-side custody of a bridged demo identity's wallet-owner keypair.

Each bridged identity's keypair is generated once by scripts/bmoni_onboard.py
(see its docstring) and held here purely as an environment variable -- never
written to disk or committed -- so BMONIClient.transfer can sign withdrawal
proposals server-side with no frontend/device signing step (Prompt 13). This
is a self-custodied wallet holding only tiny (CNGN ~1,000 / USDB ~$10)
sandbox demo funds; it is not a pattern for custody of anything real.

Env var name: BMONI_SIGNING_KEY__<seed_user_id>, e.g. BMONI_SIGNING_KEY__user_001,
where seed_user_id is the synthetic seed user the identity is bridged to in
seeds/identity_bridge.json.
"""

from __future__ import annotations

import os
from typing import Optional

from eth_account import Account
from eth_account.signers.local import LocalAccount


def _env_var_name(seed_user_id: str) -> str:
    return f"BMONI_SIGNING_KEY__{seed_user_id}"


def signing_account(seed_user_id: str) -> Optional[LocalAccount]:
    """The server-held signing account for a bridged demo identity, if configured."""
    private_key = os.environ.get(_env_var_name(seed_user_id))
    if not private_key:
        return None
    account: LocalAccount = Account.from_key(private_key)
    return account
