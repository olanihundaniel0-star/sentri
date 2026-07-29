"""Standalone BMONI sandbox onboarding script. Not part of the FastAPI app.

Run manually, once per demo identity:

    uv run python scripts/bmoni_onboard.py \\
        --name "Ada" --email ada@example.com --phone "+2348000000001"

Walks one identity through the mandatory sandbox sequence documented in the
BMONI Hackathon Quick Start: create user -> create managed smart wallet ->
check KYC -> activate the NGN rail -> poll onboarding status until active.
Then stops: test funds (CNGN 1,000 / USDB $10 per wallet) are credited
manually by BMONI staff in the room, keyed off the phone number used at
signup -- there is no funding endpoint in the sandbox API.

The wallet's owner keypair is generated locally and never sent anywhere
except as a signature; its private key is printed once at the end so it can
be held server-side for Prompt 13's transfer signing (BMONIClient.transfer
via sentri.bmoni.signing) -- store it as an env var, never commit it.
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount

from sentri.config import Config

_TEST_BVN = "22222222222"
_COUNTRY_CODE = "NGA"
_WALLET_CURRENCY = "CNGN"
_POLL_INTERVAL_SECONDS = 3.0
_POLL_MAX_ATTEMPTS = 20


def _client() -> httpx.Client:
    if not Config.BMONI_API_KEY:
        print("BMONI_API_KEY is not set in the environment", file=sys.stderr)
        raise SystemExit(1)
    return httpx.Client(
        base_url=Config.BMONI_BASE_URL,
        headers={"x-api-key": Config.BMONI_API_KEY, "Content-Type": "application/json"},
        timeout=30.0,
    )


def create_user(client: httpx.Client, first_name: str, email: str, phone: str) -> str:
    response = client.post(
        "/v1/users",
        json={"firstName": first_name, "email": email, "phoneNumber": phone},
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    return str(body["bmoniUserId"])


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

    TODO(bmoni-schema): challenge/response field names (message, challengeId,
    address, index) are best guesses pending a confirmed schema; expect to
    adjust them the first time this hits a live sandbox.
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
            "challengeId": challenge["challengeId"],
            "signature": signed.signature.hex(),
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
) -> None:
    response = client.post(
        f"/v1/users/{user_id}/onboarding/start-nigeria",
        json={
            "bvn": _TEST_BVN,
            "countryCode": _COUNTRY_CODE,
            "walletAddress": wallet_address,
            "walletIndex": wallet_index,
        },
    )
    response.raise_for_status()


def poll_until_active(client: httpx.Client, user_id: str) -> dict[str, Any]:
    for attempt in range(1, _POLL_MAX_ATTEMPTS + 1):
        status = check_onboarding_status(client, user_id)
        if status.get("status") == "active":
            return status
        print(f"  onboarding status ({attempt}/{_POLL_MAX_ATTEMPTS}): {status}")
        time.sleep(_POLL_INTERVAL_SECONDS)
    raise RuntimeError(f"onboarding did not reach 'active' after {_POLL_MAX_ATTEMPTS} polls")


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
        activate_nigeria_rail(client, user_id, wallet_address, wallet_index)

        print("Polling onboarding status until active ...")
        final_status = poll_until_active(client, user_id)
        print(f"  final status = {final_status}")

    print()
    print("Onboarding complete. Test funds have no API -- ask BMONI staff in the room")
    print("to credit this identity (CNGN 1,000 / USDB $10) using the phone number below.")
    print(f"  bmoniUserId : {user_id}")
    print(f"  phone       : {args.phone}")
    print()
    print("Wallet owner private key (needed for Prompt 13 transfer signing).")
    print("Store it server-side as an env var -- NEVER commit it or paste it into")
    print("seeds/identity_bridge.json (that file is checked into git):")
    print("  export BMONI_SIGNING_KEY__<seed_user_id>=" + account.key.hex())
    print("e.g. BMONI_SIGNING_KEY__user_001 if this identity is bridged to user_001")
    print("in seeds/identity_bridge.json.")


if __name__ == "__main__":
    main()
