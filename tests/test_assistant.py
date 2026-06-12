from dataclasses import replace
from datetime import date, datetime

from weather_assistant.assistant import PersonalAssistant
from weather_assistant.calendar_store import CalendarStore
from weather_assistant.rules_engine import RulesEngine
from tests.stubs import ROOT, StubWeatherClient


def test_briefing_includes_weather_and_events(assistant):
    output = assistant.briefing(day=date(2026, 6, 12))
    assert "Weather Briefing" in output
    assert "San Francisco" in output
    assert "Morning standup" in output
    assert "Evening run" in output


def test_weather_report(assistant):
    output = assistant.weather_report("home")
    assert "San Francisco" in output
    assert "Recommendations" in output


def test_ask_jacket(assistant):
    answer = assistant.ask("Do I need a jacket today?")
    assert "jacket" in answer.lower() or "layers" in answer.lower()


def test_ask_umbrella_with_rain(sample_snapshot, rules, calendar):
    rainy = replace(sample_snapshot, current=replace(sample_snapshot.current, precipitation_probability=55))
    stub = PersonalAssistant(
        rules, calendar, StubWeatherClient(rainy), project_root=ROOT
    )
    answer = stub.ask("umbrella?")
    assert "umbrella" in answer.lower()


def test_ask_unknown(assistant):
    answer = assistant.ask("quantum physics")
    assert "didn't understand" in answer.lower()


def test_list_events(assistant):
    output = assistant.list_events(now=datetime(2026, 6, 12, 8, 0, 0))
    assert "Upcoming events" in output
    assert "Evening run" in output


def test_cli_main_runs_briefing_with_stub(monkeypatch, sample_snapshot, rules, calendar):
    from weather_assistant import cli

    stub = PersonalAssistant(
        rules, calendar, StubWeatherClient(sample_snapshot), project_root=ROOT
    )
    monkeypatch.setattr(cli, "build_assistant", lambda root=None: stub)

    captured: list[str] = []

    def fake_print(msg: str) -> None:
        captured.append(msg)

    monkeypatch.setattr("builtins.print", fake_print)
    assert cli.main(["briefing"]) == 0
    assert "Weather Briefing" in captured[0]
