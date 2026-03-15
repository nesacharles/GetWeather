"""Google ADK weather agent — fetches weather for any city and logs it to PostgreSQL."""

import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from tools import get_weather

weather_agent = Agent(
    name="weather_agent", 
    model="gemini-2.5-flash-lite",
    description="An agent that retrieves current weather data for any city and state and stores it in a PostgreSQL database.",
    instruction=(
        "You are a helpful weather assistant. "
        "The user may ask for weather in one city or many cities at once "
        "(e.g. 'get the temperature of 10 major cities in Colorado'). "
        "For each city mentioned or implied, call the get_weather tool with the "
        "appropriate city and state. If the user asks for 'major cities' in a state, "
        "pick the most well-known cities in that state up to the requested count. "
        "Call get_weather once per city — do NOT skip any. "
        "After all calls complete, summarise the results for every city."
    ),
    tools=[get_weather],
)
