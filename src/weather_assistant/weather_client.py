from __future__ import annotations

import os
from datetime import datetime

import httpx

from weather_assistant.models import (
    CurrentWeather,
    HourlyForecast,
    Location,
    WeatherSnapshot,
)

WMO_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


class WeatherClient:
    def __init__(self, base_url: str | None = None, client: httpx.Client | None = None):
        self.base_url = base_url or os.environ.get(
            "OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1"
        )
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=15.0)
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> WeatherClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def describe_weather_code(self, code: int) -> str:
        return WMO_DESCRIPTIONS.get(code, f"Weather code {code}")

    def fetch_snapshot(self, location: Location) -> WeatherSnapshot:
        params = {
            "latitude": location.lat,
            "longitude": location.lon,
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "precipitation",
                "precipitation_probability",
                "weather_code",
                "wind_speed_10m",
            ],
            "hourly": [
                "temperature_2m",
                "apparent_temperature",
                "precipitation",
                "precipitation_probability",
                "weather_code",
                "wind_speed_10m",
            ],
            "forecast_days": 2,
            "timezone": "auto",
        }
        response = self._get_client().get(f"{self.base_url}/forecast", params=params)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        current_weather = CurrentWeather(
            temperature_c=float(current["temperature_2m"]),
            apparent_temperature_c=float(current["apparent_temperature"]),
            precipitation_probability=int(current.get("precipitation_probability") or 0),
            precipitation_mm=float(current.get("precipitation") or 0),
            wind_speed_kmh=float(current["wind_speed_10m"]),
            weather_code=int(current["weather_code"]),
            time=datetime.fromisoformat(current["time"]),
        )

        hourly: list[HourlyForecast] = []
        hourly_data = data.get("hourly", {})
        times = hourly_data.get("time", [])
        for i, time_str in enumerate(times):
            hourly.append(
                HourlyForecast(
                    time=datetime.fromisoformat(time_str),
                    temperature_c=float(hourly_data["temperature_2m"][i]),
                    apparent_temperature_c=float(
                        hourly_data["apparent_temperature"][i]
                    ),
                    precipitation_probability=int(
                        hourly_data["precipitation_probability"][i]
                    ),
                    precipitation_mm=float(hourly_data["precipitation"][i]),
                    wind_speed_kmh=float(hourly_data["wind_speed_10m"][i]),
                    weather_code=int(hourly_data["weather_code"][i]),
                )
            )

        return WeatherSnapshot(
            location=location, current=current_weather, hourly=hourly
        )

    def forecast_at(
        self, snapshot: WeatherSnapshot, target: datetime
    ) -> HourlyForecast | CurrentWeather:
        for hour in snapshot.hourly:
            if hour.time == target:
                return hour
        for hour in snapshot.hourly:
            if hour.time.date() == target.date() and hour.time.hour == target.hour:
                return hour
        return snapshot.current
