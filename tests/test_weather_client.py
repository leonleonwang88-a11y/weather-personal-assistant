from weather_assistant.models import Location
from weather_assistant.weather_client import WeatherClient


def test_fetch_snapshot(httpx_mock, open_meteo_response):
    httpx_mock.add_response(json=open_meteo_response)
    location = Location(name="home", lat=37.77, lon=-122.42, label="SF")
    client = WeatherClient(base_url="https://api.open-meteo.com/v1")

    snapshot = client.fetch_snapshot(location)

    assert snapshot.current.temperature_c == 15.2
    assert len(snapshot.hourly) == 2
    assert snapshot.hourly[1].precipitation_probability == 35
    client.close()


def test_describe_weather_code():
    client = WeatherClient()
    assert "rain" in client.describe_weather_code(61).lower()
    assert client.describe_weather_code(9999).startswith("Weather code")
