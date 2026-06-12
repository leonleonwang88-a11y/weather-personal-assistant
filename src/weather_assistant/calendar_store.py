from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from weather_assistant.models import CalendarEvent


class CalendarStore:
    def __init__(self, calendar_path: Path):
        self.calendar_path = calendar_path
        self._data = self._load(calendar_path)

    @staticmethod
    def _load(path: Path) -> dict:
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    @property
    def default_location(self) -> str:
        return self._data.get("default_location", "home")

    def events(self) -> list[CalendarEvent]:
        result: list[CalendarEvent] = []
        for raw in self._data.get("events", []):
            result.append(
                CalendarEvent(
                    id=raw["id"],
                    title=raw["title"],
                    start=datetime.fromisoformat(raw["start"]),
                    end=datetime.fromisoformat(raw["end"]),
                    location=raw.get("location", self.default_location),
                    outdoor=bool(raw.get("outdoor", False)),
                    notes=raw.get("notes", ""),
                )
            )
        return sorted(result, key=lambda e: e.start)

    def events_on(self, day: date) -> list[CalendarEvent]:
        return [e for e in self.events() if e.start.date() == day]

    def events_within(self, start: datetime, hours: int) -> list[CalendarEvent]:
        end = start + timedelta(hours=hours)
        return [e for e in self.events() if start <= e.start <= end]

    def upcoming(self, now: datetime | None = None) -> list[CalendarEvent]:
        now = now or datetime.now()
        return [e for e in self.events() if e.end >= now]
