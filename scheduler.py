"""Scheduler that invokes the ADK weather agent every hour."""

import argparse
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import weather_agent
from db import init_db

APP_NAME = "weather_app"
USER_ID = "scheduler"


async def run_agent_once(city: str, state: str):
    """Run the weather agent a single time for the given city/state."""
    session_service = InMemorySessionService()

    runner = Runner(
        agent=weather_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    user_message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=f"Fetch the current weather for {city}, {state} and store it in the database."
            )
        ],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_message,
    ):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] Agent response: {final_response}")


async def main(city: str, state: str):
    """Initialize DB and start the hourly scheduler."""
    init_db()

    # Run once immediately on startup
    print(f"Running initial weather fetch for {city}, {state}...")
    await run_agent_once(city, state)

    # Schedule every 1 hour
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_agent_once,
        trigger=IntervalTrigger(hours=1),
        args=[city, state],
        id="weather_hourly",
        name=f"Fetch weather for {city}, {state} every hour",
        replace_existing=True,
    )
    scheduler.start()
    print(f"Scheduler started — fetching weather for {city}, {state} every 1 hour. Press Ctrl+C to stop.")

    # Keep the event loop running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule hourly weather fetches.")
    parser.add_argument("--city", required=True, help="City name (e.g. Denver)")
    parser.add_argument("--state", required=True, help="State name (e.g. Colorado)")
    args = parser.parse_args()
    asyncio.run(main(args.city, args.state))
