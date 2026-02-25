"""Tests for the swim scoring engine."""

import pytest
from lib.swim_score import evaluate_conditions
from lib.constants import YES, MAYBE, NO


def _make_marine(**overrides):
    """Create marine data dict with sensible defaults."""
    base = {
        "sea_surface_temp": 26.0,
        "wave_height": 0.4,
        "wave_direction": 180,
        "wave_period": 8.0,
        "wind_wave_height": 0.2,
        "swell_wave_height": 0.3,
        "swell_wave_direction": 200,
        "swell_wave_period": 10.0,
        "ocean_current_velocity": 0.2,
        "ocean_current_direction": 90,
        "daily_max_wave": 0.6,
    }
    base.update(overrides)
    return base


def _make_weather(**overrides):
    """Create weather data dict with sensible defaults."""
    base = {
        "air_temp": 28.0,
        "apparent_temp": 30.0,
        "wind_speed": 10.0,
        "wind_gusts": 15.0,
        "wind_direction": 180,
        "precipitation": 0.0,
        "rain": 0.0,
        "uv_index": 5.0,
        "cloud_cover": 20,
        "weather_code": 1,
        "humidity": 65,
        "uv_index_max": 7.0,
        "temp_max": 30.0,
        "temp_min": 24.0,
        "precip_sum": 0.0,
        "precip_probability_max": 0,
        "sunrise": "06:30",
        "sunset": "19:45",
    }
    base.update(overrides)
    return base


class TestBeachOpen:
    """Calm seas, light wind, no storms -> beach is open (YES)."""

    def test_calm_conditions(self):
        marine = _make_marine(wave_height=0.3)
        weather = _make_weather(wind_speed=8.0)
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == YES

    def test_cold_water_still_open(self):
        """Cold water does NOT close a beach."""
        marine = _make_marine(sea_surface_temp=8.0, wave_height=0.3)
        weather = _make_weather(wind_speed=5.0)
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == YES
        assert result["factors"]["water_temp"]["verdict"] is None

    def test_high_uv_still_open(self):
        """High UV does NOT close a beach."""
        weather = _make_weather(uv_index=11.0, wind_speed=5.0)
        result = evaluate_conditions(_make_marine(), weather)
        assert result["verdict"] == YES
        assert result["factors"]["uv_index"]["verdict"] is None

    def test_verdict_has_all_fields(self):
        result = evaluate_conditions(_make_marine(), _make_weather())
        assert "verdict" in result
        assert "factors" in result
        assert "tips" in result
        assert "summary" in result

    def test_factors_have_required_keys(self):
        result = evaluate_conditions(_make_marine(), _make_weather())
        for key, factor in result["factors"].items():
            assert "value" in factor
            assert "label" in factor
            assert "verdict" in factor
            assert "bar" in factor


class TestBeachClosed:
    """Dangerous conditions -> beach is closed (NO)."""

    def test_high_waves(self):
        marine = _make_marine(wave_height=3.5)
        result = evaluate_conditions(marine, _make_weather())
        assert result["verdict"] == NO
        assert result["factors"]["wave_height"]["verdict"] == NO

    def test_extreme_wind(self):
        weather = _make_weather(wind_speed=55.0)
        result = evaluate_conditions(_make_marine(), weather)
        assert result["verdict"] == NO
        assert result["factors"]["wind_speed"]["verdict"] == NO

    def test_thunderstorm(self):
        weather = _make_weather(weather_code=95)
        result = evaluate_conditions(_make_marine(), weather)
        assert result["verdict"] == NO
        assert result["factors"]["weather_code"]["verdict"] == NO

    def test_heavy_rain(self):
        weather = _make_weather(precipitation=15.0)
        result = evaluate_conditions(_make_marine(), weather)
        assert result["verdict"] == NO

    def test_two_yellow_flags_means_red(self):
        """Two MAYBE safety factors -> NO (two yellow flags = red flag)."""
        marine = _make_marine(wave_height=1.6)        # MAYBE
        weather = _make_weather(wind_speed=35.0)       # MAYBE
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == NO


class TestCaution:
    """One borderline safety factor -> MAYBE."""

    def test_moderate_waves(self):
        marine = _make_marine(wave_height=1.6)
        weather = _make_weather(wind_speed=8.0)
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == MAYBE

    def test_moderate_wind(self):
        marine = _make_marine(wave_height=0.3)
        weather = _make_weather(wind_speed=35.0)
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == MAYBE


class TestTips:
    """Tips are generated for informational factors."""

    def test_high_uv_tip(self):
        weather = _make_weather(uv_index=9.0)
        result = evaluate_conditions(_make_marine(), weather)
        assert any("uv" in tip.lower() or "sunscreen" in tip.lower() for tip in result["tips"])

    def test_cold_water_tip(self):
        marine = _make_marine(sea_surface_temp=14.0)
        result = evaluate_conditions(marine, _make_weather())
        assert any("cold" in tip.lower() or "wetsuit" in tip.lower() for tip in result["tips"])

    def test_rough_waves_tip(self):
        marine = _make_marine(wave_height=2.0)
        result = evaluate_conditions(marine, _make_weather())
        assert any("wave" in tip.lower() or "rough" in tip.lower() for tip in result["tips"])

    def test_no_tips_perfect_conditions(self):
        marine = _make_marine(sea_surface_temp=26.0, wave_height=0.3)
        weather = _make_weather(wind_speed=8.0, uv_index=2.0, precipitation=0.0)
        result = evaluate_conditions(marine, weather)
        assert len(result["tips"]) == 0


class TestNoneValues:
    """Graceful handling of missing data."""

    def test_none_water_temp(self):
        marine = _make_marine(sea_surface_temp=None)
        result = evaluate_conditions(marine, _make_weather())
        assert result["factors"]["water_temp"]["label"] == "Unknown"

    def test_none_wave_height(self):
        marine = _make_marine(wave_height=None)
        result = evaluate_conditions(marine, _make_weather())
        assert result["factors"]["wave_height"]["label"] == "Unknown"

    def test_none_water_temp_doesnt_affect_verdict(self):
        """Missing water temp should not block swimming."""
        marine = _make_marine(sea_surface_temp=None, wave_height=0.3)
        weather = _make_weather(wind_speed=5.0)
        result = evaluate_conditions(marine, weather)
        assert result["verdict"] == YES
