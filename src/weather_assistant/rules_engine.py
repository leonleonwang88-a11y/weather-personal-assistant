from __future__ import annotations

import json
import re
from pathlib import Path

from weather_assistant.models import (
    CalendarEvent,
    CurrentWeather,
    HourlyForecast,
    Recommendation,
    WeatherSnapshot,
)


class RulesEngine:
    def __init__(self, rules_path: Path):
        self._config = self._load_config(rules_path)
        self.thresholds = self._config["thresholds"]
        self.messages = self._config["messages"]
        self.ask_patterns = self._config["ask_patterns"]
        self.locations = self._config["locations"]
        self.default_location = self._config["default_location"]

    @staticmethod
    def _load_config(rules_path: Path) -> dict:
        text = rules_path.read_text(encoding="utf-8")
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON configuration block found in {rules_path}")
        return json.loads(match.group(1))

    def location_coords(self, name: str) -> tuple[float, float, str]:
        if name not in self.locations:
            raise KeyError(f"Unknown location: {name}")
        loc = self.locations[name]
        return loc["lat"], loc["lon"], loc["label"]

    def clothing_recommendations(self, weather: CurrentWeather) -> list[Recommendation]:
        temp = weather.apparent_temperature_c or weather.temperature_c
        t = self.thresholds
        if temp <= t["cold_c"]:
            key, category = "cold", "clothing"
        elif temp <= t["cool_c"]:
            key, category = "cool", "clothing"
        elif temp <= t["warm_c"]:
            key, category = "mild", "clothing"
        elif temp <= t["hot_c"]:
            key, category = "warm", "clothing"
        else:
            key, category = "hot", "clothing"

        return [
            Recommendation(
                category=category,
                message=self.messages[key].format(temp=round(temp, 1)),
                severity="info" if key in ("mild", "warm") else "warning",
            )
        ]

    def precipitation_recommendations(self, weather: CurrentWeather) -> list[Recommendation]:
        precip = weather.precipitation_probability
        t = self.thresholds
        recs: list[Recommendation] = []

        if precip >= t["rain_chance_pct"]:
            recs.append(
                Recommendation(
                    category="rain",
                    message=self.messages["rain_likely"].format(precip=precip),
                    severity="warning",
                )
            )
        elif precip >= 20:
            recs.append(
                Recommendation(
                    category="rain",
                    message=self.messages["rain_possible"].format(precip=precip),
                    severity="info",
                )
            )

        if weather.precipitation_mm >= t["heavy_rain_mm"]:
            recs.append(
                Recommendation(
                    category="rain",
                    message=f"Heavy rain expected ({weather.precipitation_mm:.1f} mm).",
                    severity="alert",
                )
            )
        return recs

    def wind_recommendations(self, weather: CurrentWeather) -> list[Recommendation]:
        wind = weather.wind_speed_kmh
        t = self.thresholds
        if wind >= t["strong_wind_kmh"]:
            return [
                Recommendation(
                    category="wind",
                    message=self.messages["strong_wind"].format(wind=round(wind, 1)),
                    severity="alert",
                )
            ]
        if wind >= t["windy_kmh"]:
            return [
                Recommendation(
                    category="wind",
                    message=self.messages["windy"].format(wind=round(wind, 1)),
                    severity="warning",
                )
            ]
        return []

    def evaluate_weather(self, weather: CurrentWeather) -> list[Recommendation]:
        recs: list[Recommendation] = []
        recs.extend(self.clothing_recommendations(weather))
        recs.extend(self.precipitation_recommendations(weather))
        recs.extend(self.wind_recommendations(weather))
        return recs

    def evaluate_event(
        self, event: CalendarEvent, forecast: HourlyForecast | CurrentWeather
    ) -> list[Recommendation]:
        if not event.outdoor:
            return []

        temp = getattr(forecast, "apparent_temperature_c", None) or forecast.temperature_c
        precip = forecast.precipitation_probability
        wind = forecast.wind_speed_kmh
        time_str = event.start.strftime("%H:%M")
        t = self.thresholds
        recs: list[Recommendation] = []

        if precip >= t["rain_chance_pct"]:
            recs.append(
                Recommendation(
                    category="event",
                    message=self.messages["outdoor_rain"].format(
                        event=event.title, time=time_str
                    ),
                    severity="warning",
                    event_id=event.id,
                )
            )
        elif wind >= t["windy_kmh"]:
            recs.append(
                Recommendation(
                    category="event",
                    message=self.messages["outdoor_wind"].format(
                        event=event.title, time=time_str
                    ),
                    severity="warning",
                    event_id=event.id,
                )
            )
        elif temp >= t["hot_c"]:
            recs.append(
                Recommendation(
                    category="event",
                    message=self.messages["outdoor_heat"].format(
                        event=event.title, time=time_str
                    ),
                    severity="warning",
                    event_id=event.id,
                )
            )
        else:
            recs.append(
                Recommendation(
                    category="event",
                    message=self.messages["outdoor_ok"].format(event=event.title),
                    severity="info",
                    event_id=event.id,
                )
            )
        return recs

    def match_ask_intent(self, question: str) -> str | None:
        lowered = question.lower()
        for intent, keywords in self.ask_patterns.items():
            if any(keyword in lowered for keyword in keywords):
                return intent
        return None

    def answer_jacket(self, snapshot: WeatherSnapshot) -> str:
        recs = self.clothing_recommendations(snapshot.current)
        return recs[0].message if recs else "No clothing advice available."

    def answer_umbrella(self, snapshot: WeatherSnapshot) -> str:
        precip = snapshot.current.precipitation_probability
        if precip >= self.thresholds["rain_chance_pct"]:
            return self.messages["rain_likely"].format(precip=precip)
        if precip >= 20:
            return self.messages["rain_possible"].format(precip=precip)
        return "Rain is unlikely. An umbrella is probably not needed."

    def answer_run(self, snapshot: WeatherSnapshot) -> str:
        w = snapshot.current
        temp = w.apparent_temperature_c or w.temperature_c
        if temp < 5:
            return "Too cold for a comfortable run. Consider indoor exercise."
        if temp > 28:
            return "Too hot for a safe run. Run early morning or indoors."
        if w.precipitation_probability >= self.thresholds["rain_chance_pct"]:
            return "Rain is likely. Consider postponing or running indoors."
        if w.wind_speed_kmh >= self.thresholds["windy_kmh"]:
            return "Windy conditions may make running uncomfortable."
        return "Conditions look good for a run."

    def answer_commute(self, snapshot: WeatherSnapshot) -> str:
        parts = [f"Commute outlook for {snapshot.location.label}:"]
        parts.append(self.answer_jacket(snapshot))
        parts.append(self.answer_umbrella(snapshot))
        if snapshot.current.wind_speed_kmh >= self.thresholds["windy_kmh"]:
            parts.append(
                self.messages["windy"].format(
                    wind=round(snapshot.current.wind_speed_kmh, 1)
                )
            )
        return " ".join(parts)
