from datetime import date
from decimal import Decimal

from leaves.rules import count_working_days

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
