from datetime import datetime
from app.services.deadline_parser import extract_deadline


def test_iso_date_after_deadline_label():
    assert extract_deadline("Applications open now. Deadline: 2026-10-15") == datetime(2026, 10, 15)


def test_day_first_numeric_date():
    assert extract_deadline("Apply before 15/10/2026 for consideration") == datetime(2026, 10, 15)
    assert extract_deadline("Closing date: 15-10-26") == datetime(2026, 10, 15)


def test_month_name_formats():
    assert extract_deadline("Application deadline October 15, 2026") == datetime(2026, 10, 15)
    assert extract_deadline("Last date to apply: 15 October 2026") == datetime(2026, 10, 15)
    assert extract_deadline("Apply no later than Oct 15, 2026") == datetime(2026, 10, 15)


def test_amharic_label():
    assert extract_deadline("የሥራ መዘጊያ፦ 2026-10-15") == datetime(2026, 10, 15)


def test_ignores_dates_without_deadline_label():
    assert extract_deadline("The position starts on 2026-10-15 with benefits") is None


def test_returns_none_without_any_date():
    assert extract_deadline("Apply soon, deadline approaching") is None
    assert extract_deadline("") is None
    assert extract_deadline(None) is None


def test_invalid_date_values_are_ignored():
    # 15 is not a valid month
    assert extract_deadline("Deadline: 2026-15-10") is None
