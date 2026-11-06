from datetime import date
from decimal import Decimal

from leaves.rules import count_working_days

NO_HOLIDAYS = {}


def test_a_single_sunday_counts_as_zero_days():
    sunday = date(2026, 11, 22)

    assert count_working_days(sunday, sunday, NO_HOLIDAYS) == Decimal("0")
