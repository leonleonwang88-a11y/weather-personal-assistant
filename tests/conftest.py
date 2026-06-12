from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from weather_assistant.assistant import PersonalAssistant
from weather_assistant.calendar_store import CalendarStore
from weather_assistant.models import (
    CurrentWeather,
    HourlyForecast,
    Location,
    WeatherSnapshot,
)
from weather_assistant.rules_engine import RulesEngine
from weather_assistant.weather_client import WeatherClient

from tests.stubs import ROOT, StubWeatherClient


@pytest.fixture
def rules() -> RulesEngine:
    return RulesEngine(ROOT / "docs" / "rules.md")


@pytest.fixture
def calendar() -> CalendarStore:
    return CalendarStore(ROOT / "calendar.json")


@pytest.fixture
def sample_location() -> Location:
    return Location(name="home", lat=37.7749, lon=-122.4194, label="San Francisco")


@pytest.fixture
def sample_current() -> CurrentWeather:
    return CurrentWeather(
        temperature_c=15.0,
        apparent_temperature_c=14.0,
        precipitation_probability=55,
        precipitation_mm=0.5,
        wind_speed_kmh=20.0,
        weather_code=3,
        time=datetime(2026, 6, 12, 8, 0, 0),
    )


@pytest.fixture
def sample_snapshot(sample_location, sample_current) -> WeatherSnapshot:
    hourly = [
        HourlyForecast(
            time=datetime(2026, 6, 12, 12, 0, 0),
            temperature_c=18.0,
            apparent_temperature_c=17.0,
            precipitation_probability=10,
            precipitation_mm=0.0,
            wind_speed_kmh=12.0,
            weather_code=1,
        ),
        HourlyForecast(
            time=datetime(2026, 6, 12, 18, 30, 0),
            temperature_c=22.0,
            apparent_temperature_c=21.0,
            precipitation_probability=60,
            precipitation_mm=1.5,
            wind_speed_kmh=35.0,
            weather_code=61,
        ),
    ]
    return WeatherSnapshot(
        location=sample_location, current=sample_current, hourly=hourly
    )


@pytest.fixture
def assistant(rules, calendar, sample_snapshot) -> PersonalAssistant:
    return PersonalAssistant(
        rules,
        calendar,
        StubWeatherClient(sample_snapshot),
        project_root=ROOT,
    )


@pytest.fixture
def open_meteo_response() -> dict:
    return {
        "current": {
            "time": "2026-06-12T08:00",
            "temperature_2m": 15.2,
            "apparent_temperature": 14.5,
            "precipitation": 0.0,
            "precipitation_probability": 30,
            "weather_code": 2,
            "wind_speed_10m": 18.5,
        },
        "hourly": {
            "time": ["2026-06-12T08:00", "2026-06-12T09:00"],
            "temperature_2m": [15.2, 16.0],
            "apparent_temperature": [14.5, 15.0],
            "precipitation": [0.0, 0.1],
            "precipitation_probability": [30, 35],
            "weather_code": [2, 3],
            "wind_speed_10m": [18.5, 20.0],
        },
    }
