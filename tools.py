"""Tools exposed to the ADK weather agent."""

from typing import Tuple

import httpx
from db import insert_weather_record

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _geocode(city: str, state: str) -> Tuple[float, float]:
    """Resolve a city/state to (latitude, longitude) via the Open-Meteo geocoding API."""
    response = httpx.get(
        GEOCODING_URL,
        params={"name": city, "count": 10, "language": "en", "format": "json"},
        timeout=15,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Could not geocode '{city}, {state}'.")

    # Try to match by state (admin1 field), fall back to first US result, then first overall
    for r in results:
        if r.get("admin1", "").lower() == state.lower() and r.get("country_code") == "US":
            return r["latitude"], r["longitude"]
    for r in results:
        if r.get("country_code") == "US":
            return r["latitude"], r["longitude"]
    return results[0]["latitude"], results[0]["longitude"]


def get_weather(city: str, state: str) -> dict:
    """Fetch the current weather for the given city and state from the Open-Meteo API
    and store it in the PostgreSQL database.

    Args:
        city: The city name (e.g. 'Denver').
        state: The state name (e.g. 'Colorado').

    Returns:
        A dict with the current temperature and the stored database record.
    """
    try:
        lat, lon = _geocode(city, state)
    except ValueError as exc:
        return {"error": str(exc)}

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "temperature_unit": "fahrenheit",
    }

    response = httpx.get(OPEN_METEO_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    current = data.get("current_weather", {})
    temp_f = current.get("temperature")

    if temp_f is None:
        return {"error": "Could not retrieve temperature from Open-Meteo API."}

    record = insert_weather_record(
        city=city,
        state=state,
        current_temp=temp_f,
    )

    return {
        "source": "Open-Meteo",
        "location": f"{city}, {state}",
        "current_temp_f": temp_f,
        "wind_speed_mph": current.get("windspeed"),
        "wind_direction": current.get("winddirection"),
        "weather_code": current.get("weathercode"),
        "observation_time": current.get("time"),
        "db_record": record,
    }
