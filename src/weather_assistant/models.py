from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Severity = Literal["info", "warning", "alert"]


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lon: float
    label: str


@dataclass(frozen=True)
class CalendarEvent:
    id: str
    title: str
    start: datetime
    end: datetime
    location: str
    outdoor: bool
    notes: str = ""


@dataclass(frozen=True)
class CurrentWeather:
    temperature_c: float
    apparent_temperature_c: float
    precipitation_probability: int
    precipitation_mm: float
    wind_speed_kmh: float
    weather_code: int
    time: datetime


@dataclass(frozen=True)
class HourlyForecast:
    time: datetime
    temperature_c: float
    apparent_temperature_c: float
    precipitation_probability: int
    precipitation_mm: float
    wind_speed_kmh: float
    weather_code: int


@dataclass(frozen=True)
class WeatherSnapshot:
    location: Location
    current: CurrentWeather
    hourly: list[HourlyForecast] = field(default_factory=list)


@dataclass
class Recommendation:
    category: str
    message: str
    severity: Severity = "info"
    event_id: str | None = None
