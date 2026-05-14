"""Tests for gitbench.ui.format."""

from gitbench.ui.format import format_duration, human_readable, human_readable_cost


class TestHumanReadable:
    def test_small_numbers_no_suffix(self):
        assert human_readable(0) == "0"
        assert human_readable(999) == "999"

    def test_kilo(self):
        assert human_readable(1_000) == "1.0K"
        assert human_readable(1_234) == "1.2K"
        assert human_readable(9_999) == "10.0K"
        assert human_readable(999_999) == "1000.0K"

    def test_mega(self):
        assert human_readable(1_000_000) == "1.0M"
        assert human_readable(1_234_567) == "1.2M"

    def test_giga(self):
        assert human_readable(1_000_000_000) == "1.0B"
        assert human_readable(1_234_567_890) == "1.2B"

    def test_with_unit(self):
        assert human_readable(1_234, unit="tok") == "1.2K tok"
        assert human_readable(45, unit="tok") == "45 tok"


class TestHumanReadableCost:
    def test_sub_dollar(self):
        assert human_readable_cost(0.042) == "$0.04"
        assert human_readable_cost(0.0) == "$0.00"

    def test_small_dollars(self):
        assert human_readable_cost(1.234) == "$1.23"
        assert human_readable_cost(99.99) == "$99.99"

    def test_larger_dollars(self):
        assert human_readable_cost(123.45) == "$123.45"


class TestFormatDuration:
    def test_seconds_only(self):
        assert format_duration(0) == "0s"
        assert format_duration(45) == "45s"
        assert format_duration(59.9) == "59s"

    def test_minutes_and_seconds(self):
        assert format_duration(60) == "1m00s"
        assert format_duration(90) == "1m30s"
        assert format_duration(134) == "2m14s"
        assert format_duration(3_600) == "60m00s"
