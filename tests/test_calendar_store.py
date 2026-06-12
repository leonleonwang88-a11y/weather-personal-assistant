from datetime import date, datetime


def test_loads_events(calendar):
    events = calendar.events()
    assert len(events) >= 4
    assert events[0].id == "evt-001"


def test_default_location(calendar):
    assert calendar.default_location == "home"


def test_events_on(calendar):
    day = date(2026, 6, 12)
    events = calendar.events_on(day)
    titles = {e.title for e in events}
    assert "Morning standup" in titles
    assert "Evening run" in titles


def test_upcoming_filters_past(calendar):
    future = datetime(2026, 6, 13, 0, 0, 0)
    upcoming = calendar.upcoming(future)
    titles = {e.title for e in upcoming}
    assert "Weekend farmers market" in titles
    assert "Morning standup" not in titles
