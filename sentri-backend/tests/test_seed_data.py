"""Tests for the cohort-aware seed data generator."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pytest

from seeds.generator import DATA_PATH, generate_seed_data, write_seed_data

_ALL_COHORTS = {"A", "B", "C", "D", "E", "F"}

_EXPECTED_AMOUNT_RANGES_KOBO: dict[str, tuple[int, int]] = {
    "mtn_airtime": (500 * 100, 10_000 * 100),
    "glo_data_bundle": (500 * 100, 10_000 * 100),
    "airtel_recharge": (500 * 100, 10_000 * 100),
    "nine_mobile_data": (500 * 100, 10_000 * 100),
    "bolt": (1_500 * 100, 12_000 * 100),
    "uber": (1_500 * 100, 12_000 * 100),
    "chowdeck": (2_500 * 100, 18_000 * 100),
    "jumia_food": (2_500 * 100, 18_000 * 100),
    "glovo": (2_500 * 100, 18_000 * 100),
}


@pytest.fixture(scope="module")
def dataset() -> dict[str, Any]:
    write_seed_data()
    return generate_seed_data()


def test_data_file_exists_after_generation() -> None:
    written = write_seed_data()
    assert written == DATA_PATH
    assert DATA_PATH.is_file()
    assert DATA_PATH.stat().st_size > 0


def test_ten_users_generated(dataset: dict[str, Any]) -> None:
    assert len(dataset["users"]) == 10


def test_each_user_has_at_least_100_transactions(dataset: dict[str, Any]) -> None:
    for user in dataset["users"]:
        assert len(user["transactions"]) >= 100, user["user_id"]


def test_persona_ten_has_no_social_graph(dataset: dict[str, Any]) -> None:
    users_by_id = {user["user_id"]: user for user in dataset["users"]}
    persona_ten = users_by_id["user_010"]
    assert persona_ten["has_social_graph"] is False
    assert persona_ten["friends"] == []

    for user_id, user in users_by_id.items():
        if user_id != "user_010":
            assert user["has_social_graph"] is True
            assert len(user["friends"]) >= 2
            assert "user_010" not in user["friends"]


def test_transactions_are_well_formed(dataset: dict[str, Any]) -> None:
    required_keys = {"amount_kobo", "timestamp", "recipient_id", "currency", "cross_border", "memo"}
    for user in dataset["users"]:
        for txn in user["transactions"]:
            assert required_keys <= txn.keys()
            assert isinstance(txn["amount_kobo"], int)
            assert txn["amount_kobo"] > 0
            assert isinstance(txn["timestamp"], int)


def test_cases_exist_for_all_six_cohorts(dataset: dict[str, Any]) -> None:
    cohorts_seen = {test_case["cohort"] for test_case in dataset["test_cases"]}
    assert cohorts_seen == _ALL_COHORTS


def test_cohort_f_only_on_the_no_graph_persona(dataset: dict[str, Any]) -> None:
    cohort_f_cases = [tc for tc in dataset["test_cases"] if tc["cohort"] == "F"]
    assert len(cohort_f_cases) == 1
    assert cohort_f_cases[0]["user_id"] == "user_010"

    cohort_a_cases = [tc for tc in dataset["test_cases"] if tc["cohort"] == "A"]
    assert all(tc["user_id"] != "user_010" for tc in cohort_a_cases)


def test_cohort_expected_fires_match_spec(dataset: dict[str, Any]) -> None:
    expected = {"A": True, "B": True, "C": True, "D": False, "E": True, "F": True}
    for test_case in dataset["test_cases"]:
        assert test_case["expected_fires"] == expected[test_case["cohort"]], test_case["cohort"]


def test_cohort_d_is_a_new_recipient_normal_amount_and_hour(dataset: dict[str, Any]) -> None:
    for test_case in dataset["test_cases"]:
        if test_case["cohort"] != "D":
            continue
        event = test_case["event"]
        assert event["recipient_id"] == "spaces_and_co_coworking"
        assert 20_000 * 100 <= event["amount_kobo"] <= 30_000 * 100
        assert "COHORT_D_TEST" in event["memo"]


def test_cohort_b_lands_at_3am(dataset: dict[str, Any]) -> None:
    from datetime import datetime, timezone

    for test_case in dataset["test_cases"]:
        if test_case["cohort"] != "B":
            continue
        event = test_case["event"]
        dt_utc = datetime.fromtimestamp(event["timestamp"], tz=timezone.utc)
        wat_hour = (dt_utc.hour + 1) % 24
        assert wat_hour == 3


def test_cohort_a_amount_is_a_high_outlier(dataset: dict[str, Any]) -> None:
    for test_case in dataset["test_cases"]:
        if test_case["cohort"] not in ("A", "F"):
            continue
        assert test_case["event"]["amount_kobo"] >= 1_000_000 * 100


def test_amount_distributions_match_expected_ranges(dataset: dict[str, Any]) -> None:
    for user in dataset["users"]:
        for txn in user["transactions"]:
            expected_range = _EXPECTED_AMOUNT_RANGES_KOBO.get(txn["recipient_id"])
            if expected_range is None:
                continue
            low, high = expected_range
            assert low <= txn["amount_kobo"] <= high, (user["user_id"], txn)


def test_offramp_currencies_include_more_than_ngn(dataset: dict[str, Any]) -> None:
    crypto_and_expat = {
        user["user_id"]
        for user in dataset["users"]
        if user["archetype"] in ("crypto_trader", "expat_returning_funds")
    }
    currencies_seen: set[str] = set()
    for user in dataset["users"]:
        if user["user_id"] not in crypto_and_expat:
            continue
        for txn in user["transactions"]:
            currencies_seen.add(txn["currency"])

    assert currencies_seen > {"NGN"}


def test_generation_is_deterministic() -> None:
    first = generate_seed_data(seed=42)
    second = generate_seed_data(seed=42)
    assert first == second


def test_family_and_landlord_recipients_are_frequent(dataset: dict[str, Any]) -> None:
    for user in dataset["users"]:
        recipient_counts = Counter(txn["recipient_id"] for txn in user["transactions"])
        landlord_id = f"{user['user_id']}_landlord"
        assert recipient_counts[landlord_id] >= 6
