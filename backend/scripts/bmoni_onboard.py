"""Standalone BMONI sandbox onboarding script. Not part of the FastAPI app.

Run manually, once per demo identity:

    uv run python scripts/bmoni_onboard.py \\
        --name "Ada" --email ada@example.com --phone "+2348000000001"

Walks one identity through the mandatory sandbox sequence: create user ->
create managed smart wallet -> check KYC -> activate the NGN rail -> confirm
the wallet is actually readable. Field names throughout were corrected
2026-07-29/30 against the sandbox's own live OpenAPI spec (GET
/docs/openapi.json) after the original hackathon-doc guesses turned out
wrong in several places -- see git history on this file. Then stops: test
funds (CNGN 1,000 / USDB $10 per wallet) are credited manually by BMONI
staff, keyed off the phone number used at signup -- there is no funding
endpoint in the sandbox API.

The wallet's owner keypair is generated locally and never sent anywhere
except as a signature. Its private key is written to a local, gitignored
file under .bmoni_keys/ (never printed to the terminal) so it can later be
held server-side as an env var for Prompt 13's transfer signing
(BMONIClient.transfer via sentri.bmoni.signing).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount

from sentri.config import BMONI_API_KEY, BMONI_BASE_URL

_TEST_BVN = "22222222222"
_WALLET_CURRENCY = "CNGN"
_POLL_INTERVAL_SECONDS = 3.0
_POLL_MAX_ATTEMPTS = 20
_KEYS_DIR = Path(__file__).resolve().parent.parent / ".bmoni_keys"


def _client() -> httpx.Client:
    if not BMONI_API_KEY:
        print("BMONI_API_KEY is not set in the environment", file=sys.stderr)
        raise SystemExit(1)
    return httpx.Client(
        base_url=BMONI_BASE_URL,
        headers={"x-api-key": BMONI_API_KEY, "Content-Type": "application/json"},
        timeout=30.0,
    )


def create_user(client: httpx.Client, first_name: str, email: str, phone: str) -> str:
    response = client.post(
        "/v1/users",
        json={"firstName": first_name, "email": email, "phoneNumber": phone},
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    return str(body["user"]["bmoniUserId"])


def create_wallet(client: httpx.Client, user_id: str) -> tuple[dict[str, Any], LocalAccount]:
    """eth_account for the keypair + owner-proof signature.

    cNGN's own meta-transaction (ERC-2771 relayer) architecture means a
    managed wallet is designed for BMONI's backend to submit signed requests
    on the user's behalf, so an off-chain EIP-191 personal_sign is the
    reasonable default. If the sandbox rejects it, that surfaces here as a
    loud httpx.HTTPStatusError, not a silent failure -- there's no fallback
    signing path stubbed in, by design.

    Returns the wallet-creation response alongside the generated account, so
    the caller can hold onto its private key for later transfer signing
    (Prompt 13) -- the smart wallet's owner address is fixed at creation
    time, so this exact keypair is the only one that can ever sign for it.

    Confirmed live 2026-07-29 against GET /docs/openapi.json: create-managed
    wants {currency, ownerProofChallengeId, ownerProofSignature,
    userOwnerAddress} (not challengeId/signature), and the signature must be
    a 65-byte 0x-prefixed hex string -- eth_account's HexBytes.hex() in the
    pinned dependency versions omits the "0x" prefix, so it's prepended here
    explicitly (the sandbox 400s otherwise). The wallet address comes back
    as "walletAddress", not "address".
    """
    account: LocalAccount = Account.create()

    challenge_response = client.post(
        f"/v1/users/{user_id}/smart-wallets/owner-proof-challenges",
        json={"currency": _WALLET_CURRENCY, "userOwnerAddress": account.address},
    )
    challenge_response.raise_for_status()
    challenge = challenge_response.json()

    message = encode_defunct(text=challenge["message"])
    signed = Account.sign_message(message, private_key=account.key)

    create_response = client.post(
        f"/v1/users/{user_id}/smart-wallets/create-managed",
        json={
            "currency": _WALLET_CURRENCY,
            "ownerProofChallengeId": challenge["challengeId"],
            "ownerProofSignature": "0x" + signed.signature.hex(),
            "userOwnerAddress": account.address,
        },
    )
    create_response.raise_for_status()
    wallet: dict[str, Any] = create_response.json()
    return wallet, account


def check_onboarding_status(client: httpx.Client, user_id: str) -> dict[str, Any]:
    response = client.get(f"/v1/users/{user_id}/onboarding/status")
    response.raise_for_status()
    status: dict[str, Any] = response.json()
    return status


def activate_nigeria_rail(
    client: httpx.Client, user_id: str, wallet_address: str, wallet_index: int
) -> dict[str, Any]:
    """Start the Nigeria (NGN) rail. Confirmed live: the body key is
    ngnWalletAddress/ngnWalletIndex, not walletAddress/walletIndex, and there
    is no countryCode field."""
    response = client.post(
        f"/v1/users/{user_id}/onboarding/start-nigeria",
        json={
            "bvn": _TEST_BVN,
            "ngnWalletAddress": wallet_address,
            "ngnWalletIndex": wallet_index,
        },
    )
    response.raise_for_status()
    result: dict[str, Any] = response.json()
    return result


def write_key_file(user_id: str, address: str, private_key_hex: str, phone: str) -> Path:
    """Persist the wallet owner's private key to a local, gitignored file.

    Never print this key to the terminal -- terminal scrollback, shared
    screens, and recorded demos are all plausible leak vectors for a key
    that (however small the funds behind it) is a real signing credential.
    """
    _KEYS_DIR.mkdir(parents=True, exist_ok=True)
    path = _KEYS_DIR / f"{user_id}.json"
    path.write_text(
        json.dumps(
            {
                "bmoniUserId": user_id,
                "address": address,
                "privateKey": private_key_hex,
                "phone": phone,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o600)
    return path


def wait_for_ngn_wallet_ready(client: httpx.Client, user_id: str) -> dict[str, Any]:
    """Confirm the NGN rail is actually usable.

    GET .../onboarding/status never reports Nigeria-rail readiness: its
    anchorStatus/bridgeStatus/moneriumStatus/etc fields track the
    international rails (confirmed live -- they stayed "not_started" through
    a successful Nigeria-only onboarding). The real signal is whether GET
    .../smart-wallets/account/balances succeeds; in practice this was true
    immediately after start-nigeria returned, but this still polls briefly
    in case that's not always synchronous.
    """
    last_error: dict[str, Any] = {}
    for attempt in range(1, _POLL_MAX_ATTEMPTS + 1):
        response = client.get(f"/v1/users/{user_id}/smart-wallets/account/balances")
        if response.status_code == 200:
            result: dict[str, Any] = response.json()
            return result
        last_error = {"status_code": response.status_code, "body": response.text}
        print(f"  balances not ready yet ({attempt}/{_POLL_MAX_ATTEMPTS}): {last_error}")
        time.sleep(_POLL_INTERVAL_SECONDS)
    raise RuntimeError(f"NGN wallet balances never became readable: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Onboard one BMONI sandbox identity for a demo.")
    parser.add_argument("--name", required=True, help="first name for the sandbox identity")
    parser.add_argument("--email", required=True, help="unique email for this test identity")
    parser.add_argument(
        "--phone", required=True, help="unique phone number; also used for manual funding"
    )
    args = parser.parse_args()

    with _client() as client:
        print(f"Creating user {args.name} <{args.email}> ...")
        user_id = create_user(client, args.name, args.email, args.phone)
        print(f"  bmoniUserId = {user_id}")

        print("Creating managed smart wallet ...")
        wallet, account = create_wallet(client, user_id)
        wallet_address = wallet.get("address") or wallet.get("walletAddress")
        if not isinstance(wallet_address, str):
            raise RuntimeError(f"wallet creation response missing an address: {wallet!r}")
        wallet_index = wallet.get("index", 0)
        print(f"  wallet = {wallet}")

        print("Checking KYC/onboarding status ...")
        print(f"  status = {check_onboarding_status(client, user_id)}")

        print("Activating Nigeria (NGN) rail ...")
        rail_status = activate_nigeria_rail(client, user_id, wallet_address, wallet_index)
        print(f"  rail status = {rail_status}")

        print("Confirming NGN wallet is usable ...")
        balances = wait_for_ngn_wallet_ready(client, user_id)
        print(f"  balances = {balances}")

    key_path = write_key_file(user_id, account.address, account.key.hex(), args.phone)

    print()
    print("Onboarding complete. Test funds have no API -- ask BMONI staff in the room")
    print("to credit this identity (CNGN 1,000 / USDB $10) using the phone number below.")
    print(f"  bmoniUserId : {user_id}")
    print(f"  address     : {account.address}")
    print(f"  phone       : {args.phone}")
    print()
    print("Wallet owner private key written to (never printed to the terminal):")
    print(f"  {key_path}")
    print("To use it for Prompt 13 transfer signing, read its privateKey field and")
    print("export it server-side, e.g.:")
    print(f"  export BMONI_SIGNING_KEY__<seed_user_id>=$(jq -r .privateKey {key_path})")
    print("(or open the file and copy the privateKey field by hand if jq isn't installed)")
    print("e.g. BMONI_SIGNING_KEY__user_001 if this identity is bridged to user_001")
    print("in seeds/identity_bridge.json. Never commit this file or paste its contents")
    print("into seeds/identity_bridge.json (that file is checked into git).")


if __name__ == "__main__":
    main()
