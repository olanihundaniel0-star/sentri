"""Tests for sentri.api.deps dependency-injection factories.

Each factory is @lru_cache(maxsize=1): without clearing the cache before and
after every test, one test's cached client/synthesizer instance would leak
into the next test's assertions regardless of what env vars it sets.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sentri.api.deps import (
    TemplateOnlySynthesizer,
    get_bmoni_client,
    get_synthesizer,
    get_synthetic_bmoni_client,
)
from sentri.api.main import app
from sentri.bmoni.client import BMONIClient as RealBMONIClient
from sentri.bmoni.stub import InMemoryBMONIStub
from sentri.synthesizer.claude import ClaudeSynthesizer


@pytest.fixture(autouse=True)
def _clear_factory_caches() -> None:
    get_bmoni_client.cache_clear()
    get_synthetic_bmoni_client.cache_clear()
    get_synthesizer.cache_clear()
    yield
    get_bmoni_client.cache_clear()
    get_synthetic_bmoni_client.cache_clear()
    get_synthesizer.cache_clear()


def test_app_boots_and_resolves_bmoni_client_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET /debug/profile/{user_id} depends on get_bmoni_client; a 200 here
    proves the app builds and FastAPI's dependency injection actually
    resolves through deps.py, not just that the factory function works in
    isolation."""
    monkeypatch.delenv("BMONI_API_KEY", raising=False)
    monkeypatch.delenv("SENTRI_SEED_PATH", raising=False)

    with TestClient(app) as client:
        response = client.get("/debug/profile/user_001")

    assert response.status_code == 200
    assert response.json()["user_id"] == "user_001"


class TestGetSynthesizer:
    def test_falls_back_to_template_when_anthropic_api_key_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert isinstance(get_synthesizer(), TemplateOnlySynthesizer)

    def test_uses_claude_when_anthropic_api_key_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        assert isinstance(get_synthesizer(), ClaudeSynthesizer)


class TestGetBmoniClient:
    def test_falls_back_to_stub_when_bmoni_api_key_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("BMONI_API_KEY", raising=False)
        assert isinstance(get_bmoni_client(), InMemoryBMONIStub)

    def test_uses_real_client_when_bmoni_api_key_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BMONI_API_KEY", "test-bmoni-key")
        assert isinstance(get_bmoni_client(), RealBMONIClient)

    async def test_respects_sentri_seed_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("BMONI_API_KEY", raising=False)
        seed_path = tmp_path / "custom_seed.json"
        seed_path.write_text(
            json.dumps(
                {
                    "users": [
                        {
                            "user_id": "only_custom_user",
                            "friends": [],
                            "has_social_graph": False,
                            "transactions": [],
                        }
                    ]
                }
            )
        )
        monkeypatch.setenv("SENTRI_SEED_PATH", str(seed_path))

        client = get_bmoni_client()

        assert isinstance(client, InMemoryBMONIStub)
        assert await client.get_transaction_history("only_custom_user") == []
        # A user that only exists in the default seed data, not this custom
        # one, proves the custom seed path was actually used, not ignored.
        assert await client.get_transaction_history("user_001") == []


class TestGetSyntheticBmoniClient:
    def test_always_returns_stub_even_with_bmoni_api_key_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BMONI_API_KEY", "test-bmoni-key")
        assert isinstance(get_synthetic_bmoni_client(), InMemoryBMONIStub)

    async def test_respects_sentri_seed_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        seed_path = tmp_path / "custom_seed.json"
        seed_path.write_text(
            json.dumps(
                {
                    "users": [
                        {
                            "user_id": "only_custom_user",
                            "friends": [],
                            "has_social_graph": False,
                            "transactions": [],
                        }
                    ]
                }
            )
        )
        monkeypatch.setenv("SENTRI_SEED_PATH", str(seed_path))

        client = get_synthetic_bmoni_client()

        assert await client.get_transaction_history("only_custom_user") == []
        assert await client.get_transaction_history("user_001") == []
