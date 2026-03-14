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
        "When asked, use the get_weather tool to fetch the current temperature "
        "for the city and state the user specifies and store it in the database. "
        "Extract the city and state from the user's message and pass them to get_weather. "
        "After storing, report the temperature and confirm the database insert."
    ),
    tools=[get_weather],
)
