"""Tests for the server-held demo-identity signing keypair lookup."""

from __future__ import annotations

import pytest
from eth_account import Account

from sentri.bmoni.signing import signing_account


def test_signing_account_is_none_when_env_var_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BMONI_SIGNING_KEY__user_001", raising=False)
    assert signing_account("user_001") is None


def test_signing_account_loads_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = Account.create()
    monkeypatch.setenv("BMONI_SIGNING_KEY__user_001", expected.key.hex())

    account = signing_account("user_001")

    assert account is not None
    assert account.address == expected.address
