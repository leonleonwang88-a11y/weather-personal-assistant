# Weather Personal Assistant — Product Requirements Document

## Overview

The Weather Personal Assistant is a CLI-based Python application that combines live weather data, calendar events, and user-defined rules to deliver timely, actionable advice. It helps users decide what to wear, whether outdoor plans are feasible, and when weather may disrupt scheduled activities.

## Goals

- Provide accurate, location-aware weather for saved places and event locations.
- Surface proactive briefings that merge today's weather with upcoming calendar events.
- Answer on-demand questions using rule-based recommendations (no external LLM required for v1).
- Keep configuration in plain files (`calendar.json`, `docs/rules.md`) so users can edit without code changes.

## Users

- Individuals who want a lightweight daily weather briefing tied to their schedule.
- Developers who want a small, testable assistant they can extend with new rules or APIs.

## Core Features

### 1. Weather

| Requirement | Detail |
|-------------|--------|
| Data source | [Open-Meteo](https://open-meteo.com/) (no API key) |
| Current conditions | Temperature, apparent temperature, precipitation, wind, weather code |
| Forecast | Hourly (24h) and daily (7d) |
| Locations | Named locations with latitude/longitude in config |

### 2. Calendar

| Requirement | Detail |
|-------------|--------|
| Storage | `calendar.json` at project root |
| Event fields | `id`, `title`, `start`, `end`, `location`, `outdoor`, optional `notes` |
| Queries | Events for today, next N hours, and per-event weather windows |

### 3. Rules Engine

| Requirement | Detail |
|-------------|--------|
| Source | Machine-readable JSON block in `docs/rules.md` |
| Categories | Clothing, rain, wind, heat, outdoor activity, commute |
| Output | Structured recommendations with severity (`info`, `warning`, `alert`) |

### 4. Assistant Interface (CLI)

| Command | Behavior |
|---------|----------|
| `briefing` | Morning-style summary: weather per default location + event-specific advice |
| `weather <location>` | Current conditions and short forecast for a named location |
| `events` | List upcoming events with weather impact notes |
| `ask <question>` | Pattern-matched Q&A (jacket, umbrella, run, commute, etc.) |

### 5. Configuration

| File | Purpose |
|------|---------|
| `calendar.json` | Events and default location |
| `docs/rules.md` | Recommendation thresholds and messaging templates |
| `OPEN_METEO_BASE_URL` (optional env) | Override weather API base URL for testing |

## Non-Goals (v1)

- Web or mobile UI
- Multi-user accounts or authentication
- Push notifications or background scheduling
- LLM / natural-language understanding beyond keyword matching
- Historical weather analytics or radar maps

## Success Criteria

1. `pytest` passes with mocked network calls.
2. `python -m weather_assistant briefing` runs against live Open-Meteo when network is available.
3. Editing `calendar.json` or rules in `docs/rules.md` changes assistant output without code edits.
4. Recommendations reference specific thresholds from `docs/rules.md`.

## Technical Stack

- Python 3.9+
- `httpx` for HTTP
- `pytest` + `pytest-httpx` for tests
- Standard library: `argparse`, `json`, `datetime`, `re`, `pathlib`

## Project Layout

```
weather-personal-assistant/
├── calendar.json
├── docs/rules.md
├── specs/PRD.md
├── requirements.txt
├── pyproject.toml
├── src/weather_assistant/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   ├── weather_client.py
│   ├── calendar_store.py
│   ├── rules_engine.py
│   └── assistant.py
└── tests/
```

## Future Enhancements

- Geocoding for free-text locations
- Slack/Telegram bot wrapper
- Optional LLM layer for richer phrasing
- Persistent user preference profiles
