from __future__ import annotations

from datetime import datetime
from pathlib import Path

from weather_assistant.models import Location, WeatherSnapshot

ROOT = Path(__file__).resolve().parents[1]


class StubWeatherClient:
    def __init__(self, snapshot: WeatherSnapshot):
        self.snapshot = snapshot
        self.calls: list[str] = []

    def fetch_snapshot(self, location: Location) -> WeatherSnapshot:
        self.calls.append(location.name)
        return WeatherSnapshot(
            location=location,
            current=self.snapshot.current,
            hourly=self.snapshot.hourly,
        )

    def forecast_at(self, snapshot: WeatherSnapshot, target: datetime):
        for hour in snapshot.hourly:
            if hour.time == target or (
                hour.time.date() == target.date() and hour.time.hour == target.hour
            ):
                return hour
        return snapshot.current

    def close(self) -> None:
        pass
