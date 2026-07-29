"""Tests for sentri.canonical utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from sentri.canonical.numeric import canonicalize_money, canonicalize_time, extract_numeric_tokens
from sentri.canonical.timestamps import ingest_timestamp, to_wat

_WAT = ZoneInfo("Africa/Lagos")


class TestIngestTimestamp:
    def test_int_input_converts_correctly(self) -> None:
        unix_seconds = int(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc).timestamp())
        dt = ingest_timestamp(unix_seconds)
        assert dt.tzinfo == _WAT
        assert dt.year == 2026
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 13
        assert dt.minute == 0

    def test_iso_string_with_offset_converts_correctly(self) -> None:
        dt = ingest_timestamp("2026-01-15T12:00:00+00:00")
        assert dt.tzinfo == _WAT
        assert dt.hour == 13
        assert dt.minute == 0

    def test_iso_string_with_z_suffix_converts_correctly(self) -> None:
        dt = ingest_timestamp("2026-01-15T12:00:00Z")
        assert dt.tzinfo == _WAT
        assert dt.hour == 13

    def test_naive_iso_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="naive"):
            ingest_timestamp("2026-01-15T12:00:00")

    def test_already_wat_timestamps_pass_through_unchanged(self) -> None:
        original = datetime(2026, 1, 15, 9, 30, 45, 123456, tzinfo=_WAT)
        converted = ingest_timestamp("2026-01-15T09:30:45.123456+01:00")
        assert converted == original
        assert to_wat(original) == original

    def test_sub_second_precision_preserved(self) -> None:
        dt = ingest_timestamp("2026-01-15T12:00:00.123456+00:00")
        assert dt.microsecond == 123456


class TestToWat:
    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            to_wat(datetime(2026, 1, 15, 12, 0, 0))


class TestCanonicalizeMoney:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("₦450,000", 45_000_000),
            ("450000", 45_000_000),
            ("NGN 4,500.50", 450_050),
            (4_500, 450_000),
            (4_500.50, 450_050),
        ],
    )
    def test_handles_naira_representations(self, raw: str | int | float, expected: int) -> None:
        assert canonicalize_money(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "four hundred fifty thousand",
            "four hundred thousand naira",
            "NGN four fifty",
        ],
    )
    def test_returns_none_for_word_form_numbers(self, raw: str) -> None:
        assert canonicalize_money(raw) is None


class TestCanonicalizeTime:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("13:30", 810),
            ("13:30:15", 810),
            ("2:47am", 167),
            ("2:47pm", 14 * 60 + 47),
            ("12:00am", 0),
            ("12:00pm", 12 * 60),
        ],
    )
    def test_handles_24_and_12_hour_formats(self, raw: str, expected: int) -> None:
        assert canonicalize_time(raw) == expected

    @pytest.mark.parametrize("raw", ["24:00", "25:00", "13:60", "not-a-time"])
    def test_returns_none_for_invalid_times(self, raw: str) -> None:
        assert canonicalize_time(raw) is None


class TestExtractNumericTokens:
    def test_finds_money_time_and_integers_in_mixed_text(self) -> None:
        text = "You sent ₦1,000 about 5 times at 2:30pm yesterday."
        assert extract_numeric_tokens(text) == [
            ("₦1,000", "money"),
            ("5", "integer"),
            ("2:30pm", "time"),
        ]

    def test_english_sample(self) -> None:
        text = "This is ₦480,000, sent at 2:47am to a first-time recipient"
        assert extract_numeric_tokens(text) == [
            ("₦480,000", "money"),
            ("2:47am", "time"),
        ]

    def test_multi_token_sample(self) -> None:
        text = (
            "You usually send between ₦8,000 and ₦45,000 to new recipients. "
            "This is ₦480,000, at 2:47am."
        )
        assert extract_numeric_tokens(text) == [
            ("₦8,000", "money"),
            ("₦45,000", "money"),
            ("₦480,000", "money"),
            ("2:47am", "time"),
        ]
