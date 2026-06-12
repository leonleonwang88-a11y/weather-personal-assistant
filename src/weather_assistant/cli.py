from __future__ import annotations

import argparse
from pathlib import Path

from weather_assistant.assistant import PersonalAssistant
from weather_assistant.calendar_store import CalendarStore
from weather_assistant.rules_engine import RulesEngine
from weather_assistant.weather_client import WeatherClient


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_assistant(root: Path | None = None) -> PersonalAssistant:
    root = root or project_root()
    rules = RulesEngine(root / "docs" / "rules.md")
    calendar = CalendarStore(root / "calendar.json")
    weather = WeatherClient()
    return PersonalAssistant(rules, calendar, weather, project_root=root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Weather Personal Assistant — weather-aware calendar advice"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("briefing", help="Daily weather and calendar briefing")
    sub.add_parser("events", help="List upcoming events with weather notes")

    weather_parser = sub.add_parser("weather", help="Weather for a named location")
    weather_parser.add_argument(
        "location",
        nargs="?",
        default=None,
        help="Location key from rules (e.g. home, work)",
    )

    ask_parser = sub.add_parser("ask", help="Ask a weather question")
    ask_parser.add_argument("question", nargs="+", help="Your question")

    args = parser.parse_args(argv)
    assistant = build_assistant()

    try:
        if args.command == "briefing":
            print(assistant.briefing())
        elif args.command == "events":
            print(assistant.list_events())
        elif args.command == "weather":
            location = args.location or assistant.calendar.default_location
            print(assistant.weather_report(location))
        elif args.command == "ask":
            print(assistant.ask(" ".join(args.question)))
        else:
            parser.print_help()
            return 1
    finally:
        assistant.weather.close()

    return 0
