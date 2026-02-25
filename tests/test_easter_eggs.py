"""Tests for the inland easter eggs module."""

import pytest
from lib.easter_eggs import get_easter_egg, INLAND_JOKES, GENERIC_JOKES


class TestCuratedLookup:
    """Test that curated cities return their specific jokes."""

    def test_paris_exact(self):
        egg = get_easter_egg("Paris")
        assert egg["water"] == "La Seine"
        assert "Seine" in egg["joke"]
        assert egg["suggestion"] == "Nice"

    def test_london_exact(self):
        egg = get_easter_egg("London")
        assert egg["water"] == "The Thames"
        assert "Thames" in egg["joke"]

    def test_cairo_exact(self):
        egg = get_easter_egg("Cairo")
        assert egg["water"] == "The Nile"
        assert "Nile" in egg["joke"]

    def test_full_location_string(self):
        """Should match on the city part of 'City, Region, Country'."""
        egg = get_easter_egg("Paris, Ile-de-France, France")
        assert egg["water"] == "La Seine"

    def test_case_insensitive(self):
        egg = get_easter_egg("PARIS")
        assert egg["water"] == "La Seine"

    def test_all_curated_cities_have_required_fields(self):
        for city, data in INLAND_JOKES.items():
            assert "water" in data, f"{city} missing 'water'"
            assert "joke" in data, f"{city} missing 'joke'"
            assert "suggestion" in data, f"{city} missing 'suggestion'"
            assert len(data["joke"]) > 20, f"{city} joke too short"


class TestGenericFallback:
    """Test that unknown inland cities get a generic joke."""

    def test_unknown_city_returns_joke(self):
        egg = get_easter_egg("Timbuktu")
        assert "joke" in egg
        assert len(egg["joke"]) > 10

    def test_unknown_city_no_water_body(self):
        egg = get_easter_egg("Timbuktu")
        assert egg.get("water") is None

    def test_generic_is_consistent(self):
        """Same city should always get the same generic joke."""
        egg1 = get_easter_egg("Timbuktu")
        egg2 = get_easter_egg("Timbuktu")
        assert egg1["joke"] == egg2["joke"]

    def test_different_cities_can_differ(self):
        """Different cities may get different generic jokes."""
        # Just verify no crash -- different inputs produce valid output
        for city in ["Timbuktu", "Kathmandu", "Denver", "Zurich", "Nairobi"]:
            egg = get_easter_egg(city)
            assert "joke" in egg

    def test_all_generic_jokes_have_content(self):
        for i, joke in enumerate(GENERIC_JOKES):
            assert "joke" in joke, f"Generic joke {i} missing 'joke'"
            assert len(joke["joke"]) > 10, f"Generic joke {i} too short"
