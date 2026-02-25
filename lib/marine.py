"""
Open-Meteo Marine API client: sea surface temperature, waves, currents.
"""

import requests

MARINE_API_URL = "https://marine-api.open-meteo.com/v1/marine"


class MarineDataError(Exception):
    pass


class NoMarineData(MarineDataError):
    """Location is too far from the ocean."""
    pass


def fetch_marine_data(latitude: float, longitude: float, timezone: str = "auto") -> dict:
    """
    Fetch current marine conditions from Open-Meteo Marine API.

    Returns:
        {
            "sea_surface_temp": 26.0,       # °C
            "wave_height": 0.5,             # meters
            "wave_direction": 180,           # degrees
            "wave_period": 8.0,             # seconds
            "swell_wave_height": 0.3,       # meters
            "ocean_current_velocity": 0.2,  # km/h
        }
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join([
            "wave_height",
            "wave_direction",
            "wave_period",
            "wind_wave_height",
            "swell_wave_height",
            "swell_wave_direction",
            "swell_wave_period",
            "ocean_current_velocity",
            "ocean_current_direction",
            "sea_surface_temperature",
        ]),
        "daily": "wave_height_max,wave_direction_dominant",
        "timezone": timezone,
        "forecast_days": 1,
        "cell_selection": "sea",
    }

    try:
        resp = requests.get(MARINE_API_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise MarineDataError(f"Marine API request failed: {e}") from e

    data = resp.json()

    if "error" in data and data["error"]:
        reason = data.get("reason", "Unknown error")
        if "no data" in reason.lower() or "out of" in reason.lower():
            raise NoMarineData(
                "This location is too far from the ocean. "
                "Try a coastal city (e.g., Miami, Barcelona, Sydney)."
            )
        raise MarineDataError(f"Marine API error: {reason}")

    current = data.get("current", {})

    sea_surface_temp = current.get("sea_surface_temperature")
    wave_height = current.get("wave_height")

    # If both key marine fields are null, the location is too far inland
    if sea_surface_temp is None and wave_height is None:
        raise NoMarineData(
            "This location is too far from the ocean for swim conditions. "
            "Try a coastal city (e.g., Miami, Barcelona, Sydney)."
        )

    return {
        "sea_surface_temp": sea_surface_temp,
        "wave_height": wave_height,
        "wave_direction": current.get("wave_direction"),
        "wave_period": current.get("wave_period"),
        "wind_wave_height": current.get("wind_wave_height"),
        "swell_wave_height": current.get("swell_wave_height"),
        "swell_wave_direction": current.get("swell_wave_direction"),
        "swell_wave_period": current.get("swell_wave_period"),
        "ocean_current_velocity": current.get("ocean_current_velocity"),
        "ocean_current_direction": current.get("ocean_current_direction"),
        "daily_max_wave": _extract_daily_max(data),
    }


def _extract_daily_max(data: dict) -> float | None:
    """Extract today's max wave height from daily data."""
    daily = data.get("daily", {})
    max_waves = daily.get("wave_height_max", [])
    if max_waves:
        return max_waves[0]
    return None
