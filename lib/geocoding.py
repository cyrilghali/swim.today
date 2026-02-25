"""
Geocoding: convert location names to lat/lon using Open-Meteo Geocoding API.
"""

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


class GeocodingError(Exception):
    pass


class LocationNotFound(GeocodingError):
    pass


def geocode(location_name: str) -> dict:
    """
    Resolve a location name to coordinates and metadata.

    Returns:
        {
            "name": "Miami Beach",
            "country": "United States",
            "admin1": "Florida",
            "latitude": 25.7907,
            "longitude": -80.1300,
            "timezone": "America/New_York",
            "population": 92312,
        }
    """
    params = {
        "name": location_name,
        "count": 5,
        "language": "en",
        "format": "json",
    }

    try:
        resp = requests.get(GEOCODING_URL, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise GeocodingError(f"Geocoding request failed: {e}") from e

    data = resp.json()

    if "results" not in data or len(data["results"]) == 0:
        raise LocationNotFound(
            f"Location not found: '{location_name}'. "
            "Try a city name near the beach (e.g., Miami, Barcelona, Sydney)."
        )

    # Prefer coastal/populated results - take the first match
    result = data["results"][0]

    return {
        "name": result.get("name", location_name),
        "country": result.get("country", ""),
        "admin1": result.get("admin1", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "timezone": result.get("timezone", "UTC"),
        "population": result.get("population", 0),
    }


def format_location(geo: dict) -> str:
    """Format location as 'Name, Region, Country'."""
    parts = [geo["name"]]
    if geo.get("admin1"):
        parts.append(geo["admin1"])
    if geo.get("country"):
        parts.append(geo["country"])
    return ", ".join(parts)
