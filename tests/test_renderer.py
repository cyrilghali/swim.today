"""Tests for the renderer module."""

import pytest
from lib.renderer import render_ansi, render_short, render_json, _strip_ansi
from lib.swim_score import evaluate_conditions


def _make_marine(**overrides):
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


def _make_geo():
    return {
        "name": "Miami",
        "country": "United States",
        "admin1": "Florida",
        "latitude": 25.7907,
        "longitude": -80.13,
    }


class TestAnsiRenderer:
    def test_contains_location(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_ansi("Miami, Florida, United States", score, marine, weather)
        assert "Miami" in _strip_ansi(output)

    def test_contains_verdict(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_ansi("Miami", score, marine, weather)
        plain = _strip_ansi(output)
        assert any(v in plain for v in ["Y E S !", "M A Y B E", "N O"])

    def test_contains_water_temp(self):
        marine = _make_marine(sea_surface_temp=26.0)
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_ansi("Miami", score, marine, weather)
        plain = _strip_ansi(output)
        assert "26" in plain
        assert "Water Temp" in plain

    def test_contains_bar_characters(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_ansi("Miami", score, marine, weather)
        # Should contain ASCII bar fill characters
        assert "#" in output or "-" in output

    def test_contains_footer(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_ansi("Miami", score, marine, weather)
        assert "swim.today" in _strip_ansi(output)


class TestShortRenderer:
    def test_one_line_output(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_short("Miami", score, marine, weather)
        lines = output.strip().split("\n")
        assert len(lines) == 1

    def test_contains_verdict(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_short("Miami", score, marine, weather)
        assert any(v in output for v in ["YES", "MAYBE", "NO"])

    def test_contains_location(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        output = render_short("Miami", score, marine, weather)
        assert "Miami" in output


class TestJsonRenderer:
    def test_has_required_fields(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        geo = _make_geo()
        output = render_json("Miami", geo, score, marine, weather)
        assert "location" in output
        assert "verdict" in output
        assert "summary" in output
        assert "conditions" in output
        assert "factors" in output

    def test_location_fields(self):
        marine = _make_marine()
        weather = _make_weather()
        score = evaluate_conditions(marine, weather)
        geo = _make_geo()
        output = render_json("Miami", geo, score, marine, weather)
        assert output["location"]["name"] == "Miami"
        assert output["location"]["country"] == "United States"

    def test_conditions_fields(self):
        marine = _make_marine(sea_surface_temp=26.0)
        weather = _make_weather(uv_index=5.0)
        score = evaluate_conditions(marine, weather)
        geo = _make_geo()
        output = render_json("Miami", geo, score, marine, weather)
        assert output["conditions"]["water_temperature_c"] == 26.0
        assert output["conditions"]["uv_index"] == 5.0


class TestStripAnsi:
    def test_strips_color_codes(self):
        text = "\033[91mHello\033[0m"
        assert _strip_ansi(text) == "Hello"

    def test_preserves_plain_text(self):
        text = "Hello World"
        assert _strip_ansi(text) == "Hello World"
