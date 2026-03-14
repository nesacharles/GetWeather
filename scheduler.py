"""Scheduler that invokes the ADK weather agent every hour."""
 
import asyncio
import os
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


async def run_agent_once():
    """Run the weather agent a single time and print the result."""
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
                text="Fetch the current weather for Parker, Colorado and store it in the database."
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


async def main():
    """Initialize DB and start the hourly scheduler."""
    init_db()

    # Run once immediately on startup
    print("Running initial weather fetch...")
    await run_agent_once()

    # Schedule every 1 hour
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_agent_once,
        trigger=IntervalTrigger(hours=1),
        id="weather_hourly",
        name="Fetch weather every hour",
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler started — fetching weather every 1 hour. Press Ctrl+C to stop.")

    # Keep the event loop running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())
