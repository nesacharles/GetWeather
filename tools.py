"""Tools exposed to the ADK weather agent."""

import httpx
from db import insert_weather_record

# Parker, Colorado coordinates
PARKER_LAT = 39.5186
PARKER_LON = -104.7614
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city: str = "Parker", state: str = "Colorado") -> dict:
    """Fetch the current weather for Parker, Colorado from the Open-Meteo API
    and store it in the PostgreSQL database.

    Args:
        city: The city name (default: Parker).
        state: The state name (default: Colorado).

    Returns:
        A dict with the current temperature and the stored database record.
    """
    params = {
        "latitude": PARKER_LAT,
        "longitude": PARKER_LON,
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
