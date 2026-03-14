# GetWeather — Google ADK Agent

A Google ADK agent that fetches current weather data for **Parker, Colorado** using the [Open-Meteo API](https://open-meteo.com/) and stores it in a PostgreSQL table every hour.

## Project Structure
 
```
GetWeather/
├── agent.py          # ADK agent definition
├── tools.py          # Weather API tool (Open-Meteo + DB insert)
├── db.py             # PostgreSQL setup and helpers
├── scheduler.py      # APScheduler — runs the agent every 1 hour
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── README.md
```

## Prerequisites

- Python 3.10+
- PostgreSQL running locally (or remotely)
- A Google Gemini API key ([get one here](https://ai.google.dev/))

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable            | Description                          |
| ------------------- | ------------------------------------ |
| `GOOGLE_API_KEY`    | Your Gemini API key                  |
| `POSTGRES_HOST`     | PostgreSQL host (default: localhost) |
| `POSTGRES_PORT`     | PostgreSQL port (default: 5432)      |
| `POSTGRES_DB`       | Database name (default: weather_db)  |
| `POSTGRES_USER`     | DB user (default: postgres)          |
| `POSTGRES_PASSWORD` | DB password                          |

### 4. Create the PostgreSQL database

```bash
createdb weather_db
```

Or via `psql`:

```sql
CREATE DATABASE weather_db;
```

### 5. Initialize the table

```bash
python db.py
```

This creates the `weather_log` table:

| Column       | Type         | Description             |
| ------------ | ------------ | ----------------------- |
| id           | SERIAL (PK)  | Auto-increment ID       |
| date_time    | TIMESTAMPTZ  | Timestamp of the record |
| city         | VARCHAR(100) | City name (Parker)      |
| state        | VARCHAR(100) | State name (Colorado)   |
| current_temp | NUMERIC(5,2) | Temperature in °F       |

## Running

### Run the hourly scheduler

```bash
python scheduler.py
```

This will:

1. Initialize the database table (if not already created)
2. Immediately fetch and store the current weather
3. Repeat every **1 hour**

### Run the agent interactively (ADK dev UI)

```bash
adk web
```

Then open the browser and select `weather_agent` to chat with it.

### One-off test

```python
from tools import get_weather
result = get_weather()
print(result)
```

## Weather API

Uses [Open-Meteo](https://open-meteo.com/) — a free, open-source weather API. **No API key required** for weather data. Coordinates for Parker, CO: `39.5186, -104.7614`.

## Querying stored data

```sql
SELECT date_time, city, state, current_temp
FROM weather_log
ORDER BY date_time DESC
LIMIT 10;
```
