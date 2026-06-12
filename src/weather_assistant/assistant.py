from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from weather_assistant.calendar_store import CalendarStore
from weather_assistant.models import Location, Recommendation, WeatherSnapshot
from weather_assistant.rules_engine import RulesEngine
from weather_assistant.weather_client import WeatherClient


class PersonalAssistant:
    def __init__(
        self,
        rules: RulesEngine,
        calendar: CalendarStore,
        weather: WeatherClient,
        project_root: Path | None = None,
    ):
        self.rules = rules
        self.calendar = calendar
        self.weather = weather
        self.project_root = project_root or Path.cwd()

    def _make_location(self, name: str) -> Location:
        lat, lon, label = self.rules.location_coords(name)
        return Location(name=name, lat=lat, lon=lon, label=label)

    def get_weather(self, location_name: str | None = None) -> WeatherSnapshot:
        name = location_name or self.calendar.default_location
        return self.weather.fetch_snapshot(self._make_location(name))

    def briefing(self, day: date | None = None) -> str:
        day = day or date.today()
        default_name = self.calendar.default_location
        snapshot = self.get_weather(default_name)
        lines: list[str] = [
            f"=== Weather Briefing for {day.isoformat()} ===",
            "",
            self._format_snapshot_header(snapshot),
            "",
            "General recommendations:",
        ]

        for rec in self.rules.evaluate_weather(snapshot.current):
            lines.append(f"  [{rec.severity}] {rec.message}")

        events = self.calendar.events_on(day)
        if not events:
            lines.append("")
            lines.append("No calendar events today.")
            return "\n".join(lines)

        lines.append("")
        lines.append("Today's events:")
        for event in events:
            loc_name = event.location or default_name
            event_snapshot = self.get_weather(loc_name)
            forecast = self.weather.forecast_at(event_snapshot, event.start)
            lines.append(
                f"  • {event.start.strftime('%H:%M')} — {event.title} "
                f"({'outdoor' if event.outdoor else 'indoor'} @ {loc_name})"
            )
            for rec in self.rules.evaluate_event(event, forecast):
                lines.append(f"      [{rec.severity}] {rec.message}")

        return "\n".join(lines)

    def list_events(self, now: datetime | None = None) -> str:
        now = now or datetime.now()
        upcoming = self.calendar.upcoming(now)
        if not upcoming:
            return "No upcoming events."

        lines = ["Upcoming events:"]
        for event in upcoming:
            loc_name = event.location or self.calendar.default_location
            snapshot = self.get_weather(loc_name)
            forecast = self.weather.forecast_at(snapshot, event.start)
            lines.append(
                f"  • {event.start.strftime('%Y-%m-%d %H:%M')} — {event.title} "
                f"({'outdoor' if event.outdoor else 'indoor'} @ {loc_name})"
            )
            if event.outdoor:
                for rec in self.rules.evaluate_event(event, forecast):
                    lines.append(f"      [{rec.severity}] {rec.message}")
        return "\n".join(lines)

    def weather_report(self, location_name: str) -> str:
        snapshot = self.get_weather(location_name)
        lines = [
            self._format_snapshot_header(snapshot),
            "",
            "Recommendations:",
        ]
        for rec in self.rules.evaluate_weather(snapshot.current):
            lines.append(f"  [{rec.severity}] {rec.message}")
        return "\n".join(lines)

    def ask(self, question: str) -> str:
        intent = self.rules.match_ask_intent(question)
        if intent is None:
            return (
                "I didn't understand that question. Try asking about a jacket, "
                "umbrella, run, or commute."
            )

        snapshot = self.get_weather()
        handlers = {
            "jacket": self.rules.answer_jacket,
            "umbrella": self.rules.answer_umbrella,
            "run": self.rules.answer_run,
            "commute": self.rules.answer_commute,
        }
        return handlers[intent](snapshot)

    @staticmethod
    def _format_snapshot_header(snapshot: WeatherSnapshot) -> str:
        w = snapshot.current
        temp = w.apparent_temperature_c or w.temperature_c
        return (
            f"{snapshot.location.label}: {temp:.1f}°C "
            f"(precip {w.precipitation_probability}%, "
            f"wind {w.wind_speed_kmh:.1f} km/h)"
        )

    def recommendations_for(
        self, snapshot: WeatherSnapshot
    ) -> list[Recommendation]:
        return self.rules.evaluate_weather(snapshot.current)
