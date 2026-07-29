"""Tests for the in-memory BMONI stub."""

from __future__ import annotations

import pytest

from sentri.bmoni.stub import InMemoryBMONIStub


@pytest.fixture(scope="module")
def stub() -> InMemoryBMONIStub:
    return InMemoryBMONIStub()


async def test_stub_loads_without_error(stub: InMemoryBMONIStub) -> None:
    assert stub is not None


async def test_get_transaction_history_returns_non_empty_for_user_001(
    stub: InMemoryBMONIStub,
) -> None:
    history = await stub.get_transaction_history("user_001")
    assert len(history) > 0


async def test_get_social_graph_returns_none_for_no_graph_persona(
    stub: InMemoryBMONIStub,
) -> None:
    assert await stub.get_social_graph("user_010") is None


async def test_get_social_graph_returns_populated_graph_for_others(
    stub: InMemoryBMONIStub,
) -> None:
    graph = await stub.get_social_graph("user_001")
    assert graph is not None
    assert graph.user_id == "user_001"
    assert len(graph.friends) > 0
    assert len(graph.friends_of_friends) > 0
    for friend_id in graph.friends:
        assert friend_id in graph.friends_of_friends
