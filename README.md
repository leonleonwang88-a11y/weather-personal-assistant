# Weather Personal Assistant

A rule-based Python CLI that combines live weather (Open-Meteo), your calendar (`calendar.json`), and configurable thresholds (`docs/rules.md`) to deliver actionable daily advice.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Daily briefing
python -m weather_assistant briefing

# Weather for a location
python -m weather_assistant weather home

# Upcoming events with weather notes
python -m weather_assistant events

# Ask a question
python -m weather_assistant ask "Do I need a jacket?"
```

## Configuration

| File | Purpose |
|------|---------|
| [`calendar.json`](calendar.json) | Events and default location |
| [`docs/rules.md`](docs/rules.md) | Thresholds, locations, and message templates (JSON block) |
| [`specs/PRD.md`](specs/PRD.md) | Product requirements |

Edit the JSON block in `docs/rules.md` to change temperature thresholds, locations, or messages. Add events to `calendar.json` — no code changes required.

## Commands

| Command | Description |
|---------|-------------|
| `briefing` | Today's weather plus event-specific outdoor advice |
| `weather [location]` | Current conditions and recommendations |
| `events` | Upcoming calendar events with weather impact |
| `ask <question>` | Keyword-based Q&A (jacket, umbrella, run, commute) |

## Project structure

```
src/weather_assistant/   Application package
tests/                   Automated tests (pytest + mocked HTTP)
docs/rules.md            Recommendation rules
specs/PRD.md             Product spec
calendar.json            Sample calendar data
```

## Environment

- `OPEN_METEO_BASE_URL` — optional override for the weather API (useful in tests)

## Requirements

- Python 3.9+
- Network access for live weather commands (tests use mocks)
