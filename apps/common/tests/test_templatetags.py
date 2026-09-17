"""Tests for shared template tags/filters."""

from apps.common.templatetags.common_extras import split


class TestSplitFilter:
    def test_splits_and_trims(self):
        assert split("Dashboard, Profile , Edit") == [
            "Dashboard",
            "Profile",
            "Edit",
        ]

    def test_empty_string_returns_empty_list(self):
        assert split("") == []

    def test_custom_separator(self):
        assert split("a|b|c", "|") == ["a", "b", "c"]
