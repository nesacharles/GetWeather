"""Database setup and connection utilities for the weather agent."""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "weather_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "charLes4$"),
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_log (
    id SERIAL PRIMARY KEY,
    date_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    current_temp NUMERIC(5, 2) NOT NULL
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_weather_log_date_time ON weather_log (date_time);
"""


def get_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create the weather_log table if it doesn't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute(CREATE_INDEX_SQL)
        conn.commit()
        print("Database initialized — weather_log table ready.")
    finally:
        conn.close()


def insert_weather_record(city: str, state: str, current_temp: float) -> dict:
    """Insert a weather record into the weather_log table.

    Returns the inserted row as a dict.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO weather_log (city, state, current_temp)
                VALUES (%s, %s, %s)
                RETURNING id, date_time, city, state, current_temp;
                """,
                (city, state, current_temp),
            )
            row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "date_time": row[1].isoformat(),
            "city": row[2],
            "state": row[3],
            "current_temp": float(row[4]),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
