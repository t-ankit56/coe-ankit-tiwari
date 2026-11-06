from datetime import date
from decimal import Decimal

import pytest

from leaves.rules import DayInRange, count_working_days, explain_each_day

NO_HOLIDAYS = {}


def test_a_single_sunday_counts_as_zero_days():
    sunday = date(2026, 11, 22)

    assert count_working_days(sunday, sunday, NO_HOLIDAYS) == Decimal("0")


def test_a_single_public_holiday_counts_as_zero_days():
    thanksgiving = date(2026, 11, 27)

    assert count_working_days(thanksgiving, thanksgiving, {thanksgiving: "Thanksgiving"}) == Decimal("0")


def test_a_single_weekday_counts_as_one_day():
    monday = date(2026, 11, 23)

    assert count_working_days(monday, monday, NO_HOLIDAYS) == Decimal("1")


def test_monday_to_friday_counts_as_five_days():
    assert count_working_days(date(2026, 11, 23), date(2026, 11, 27), NO_HOLIDAYS) == Decimal("5")


def test_a_weekend_inside_the_range_is_not_counted():
    assert count_working_days(date(2026, 12, 24), date(2026, 12, 28), NO_HOLIDAYS) == Decimal("3")


@pytest.mark.parametrize(
    "start_date, end_date, holidays, expected_days",
    [
        (date(2026, 11, 23), date(2026, 11, 27), {date(2026, 11, 27): "Thanksgiving"}, "4"),
        (date(2026, 12, 24), date(2026, 12, 28), {date(2026, 12, 25): "Christmas"}, "2"),
    ],
)
def test_public_holidays_inside_the_range_are_not_counted(start_date, end_date, holidays, expected_days):
    assert count_working_days(start_date, end_date, holidays) == Decimal(expected_days)


def test_range_starting_and_ending_on_a_weekend_counts_only_the_weekdays():
    assert count_working_days(date(2026, 11, 21), date(2026, 11, 29), NO_HOLIDAYS) == Decimal("5")


def test_range_crossing_a_month_end_is_counted_across_both_months():
    assert count_working_days(date(2026, 11, 30), date(2026, 12, 1), NO_HOLIDAYS) == Decimal("2")


def test_range_crossing_a_year_end_is_counted_across_both_years():
    new_year = {date(2027, 1, 1): "New Year"}

    assert count_working_days(date(2026, 12, 31), date(2027, 1, 1), new_year) == Decimal("1")


def test_a_half_day_on_a_working_day_counts_as_half_a_day():
    thursday = date(2026, 11, 19)

    assert count_working_days(thursday, thursday, NO_HOLIDAYS, half_day=True) == Decimal("0.5")


def test_each_day_says_whether_it_counts_and_why_not():
    thanksgiving = {date(2026, 11, 27): "Thanksgiving"}

    breakdown = explain_each_day(date(2026, 11, 21), date(2026, 11, 27), thanksgiving)

    assert breakdown == [
        DayInRange(date(2026, 11, 21), Decimal("0"), "Weekend"),
        DayInRange(date(2026, 11, 22), Decimal("0"), "Weekend"),
        DayInRange(date(2026, 11, 23), Decimal("1"), None),
        DayInRange(date(2026, 11, 24), Decimal("1"), None),
        DayInRange(date(2026, 11, 25), Decimal("1"), None),
        DayInRange(date(2026, 11, 26), Decimal("1"), None),
        DayInRange(date(2026, 11, 27), Decimal("0"), "Thanksgiving, not counted"),
    ]
