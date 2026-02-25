"""
Open-Meteo Weather API client: air temperature, wind, UV, precipitation.
"""

import requests

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherDataError(Exception):
    pass


def fetch_weather_data(latitude: float, longitude: float, timezone: str = "auto") -> dict:
    """
    Fetch current weather conditions from Open-Meteo Weather API.

    Returns:
        {
            "air_temp": 29.0,               # °C
            "apparent_temp": 32.0,           # °C (feels like)
            "wind_speed": 12.0,             # km/h
            "wind_gusts": 20.0,             # km/h
            "wind_direction": 180,           # degrees
            "precipitation": 0.0,           # mm
            "uv_index": 7.0,
            "cloud_cover": 25,              # %
            "weather_code": 1,              # WMO code
            "humidity": 65,                 # %
            "visibility": 24140,            # meters
        }
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m",
            "precipitation",
            "rain",
            "uv_index",
            "cloud_cover",
            "weather_code",
            "relative_humidity_2m",
        ]),
        "daily": ",".join([
            "uv_index_max",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
        ]),
        "timezone": timezone,
        "forecast_days": 1,
    }

    try:
        resp = requests.get(WEATHER_API_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise WeatherDataError(f"Weather API request failed: {e}") from e

    data = resp.json()

    if "error" in data and data["error"]:
        raise WeatherDataError(f"Weather API error: {data.get('reason', 'Unknown')}")

    current = data.get("current", {})
    daily = data.get("daily", {})

    return {
        "air_temp": current.get("temperature_2m"),
        "apparent_temp": current.get("apparent_temperature"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_gusts": current.get("wind_gusts_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "precipitation": current.get("precipitation", 0),
        "rain": current.get("rain", 0),
        "uv_index": current.get("uv_index"),
        "cloud_cover": current.get("cloud_cover"),
        "weather_code": current.get("weather_code", 0),
        "humidity": current.get("relative_humidity_2m"),
        "uv_index_max": _safe_first(daily.get("uv_index_max")),
        "temp_max": _safe_first(daily.get("temperature_2m_max")),
        "temp_min": _safe_first(daily.get("temperature_2m_min")),
        "precip_sum": _safe_first(daily.get("precipitation_sum")),
        "precip_probability_max": _safe_first(daily.get("precipitation_probability_max")),
        "sunrise": _safe_first(daily.get("sunrise")),
        "sunset": _safe_first(daily.get("sunset")),
    }


def _safe_first(lst):
    """Safely get the first element of a list or return None."""
    if lst and len(lst) > 0:
        return lst[0]
    return None
