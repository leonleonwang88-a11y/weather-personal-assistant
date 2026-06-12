from datetime import datetime

from weather_assistant.models import CalendarEvent, CurrentWeather, HourlyForecast


def test_loads_config_from_rules_md(rules):
    assert rules.default_location == "home"
    assert "cold_c" in rules.thresholds
    assert "jacket" in rules.ask_patterns


def test_clothing_cold(rules):
    weather = CurrentWeather(
        temperature_c=8.0,
        apparent_temperature_c=7.0,
        precipitation_probability=0,
        precipitation_mm=0.0,
        wind_speed_kmh=5.0,
        weather_code=0,
        time=datetime.now(),
    )
    recs = rules.clothing_recommendations(weather)
    assert len(recs) == 1
    assert "jacket" in recs[0].message.lower()


def test_rain_likely_warning(rules):
    weather = CurrentWeather(
        temperature_c=18.0,
        apparent_temperature_c=18.0,
        precipitation_probability=50,
        precipitation_mm=0.0,
        wind_speed_kmh=10.0,
        weather_code=61,
        time=datetime.now(),
    )
    recs = rules.precipitation_recommendations(weather)
    assert any(r.severity == "warning" for r in recs)


def test_outdoor_event_rain(rules):
    event = CalendarEvent(
        id="e1",
        title="Picnic",
        start=datetime(2026, 6, 12, 18, 30),
        end=datetime(2026, 6, 12, 19, 30),
        location="home",
        outdoor=True,
    )
    forecast = HourlyForecast(
        time=datetime(2026, 6, 12, 18, 30),
        temperature_c=20.0,
        apparent_temperature_c=20.0,
        precipitation_probability=60,
        precipitation_mm=1.0,
        wind_speed_kmh=10.0,
        weather_code=61,
    )
    recs = rules.evaluate_event(event, forecast)
    assert recs[0].severity == "warning"
    assert "Picnic" in recs[0].message


def test_match_ask_intent(rules):
    assert rules.match_ask_intent("Do I need a jacket?") == "jacket"
    assert rules.match_ask_intent("Should I bring an umbrella") == "umbrella"
    assert rules.match_ask_intent("good for a run tonight") == "run"
    assert rules.match_ask_intent("how is my commute") == "commute"
    assert rules.match_ask_intent("what is the meaning of life") is None
