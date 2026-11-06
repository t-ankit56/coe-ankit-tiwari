from dataclasses import asdict
from datetime import date
from decimal import Decimal

import pytest

from leaves.rules import LeaveRecord, MonthUsage, SuggestedRequest, check_probation_limit

HOLIDAYS = {
    date(2026, 11, 27): "Thanksgiving",
    date(2026, 12, 25): "Christmas",
    date(2027, 1, 1): "New Year",
}


def approved(start_date, end_date, half_day=False, status="approved"):
    return LeaveRecord(id=None, start_date=start_date, end_date=end_date, half_day=half_day, status=status)


# Aarav's screen: 1.5 days already used in November 2026.
AARAV_USED = [
    approved(date(2026, 11, 2), date(2026, 11, 2)),
    approved(date(2026, 11, 3), date(2026, 11, 3), half_day=True),
]


def check(start_date, end_date, existing=(), half_day=False, on_probation=True):
    return check_probation_limit(
        on_probation=on_probation,
        start_date=start_date,
        end_date=end_date,
        half_day=half_day,
        existing=list(existing),
        holidays=HOLIDAYS,
    )


def test_user_not_on_probation_is_never_limited():
    status = check(date(2026, 11, 9), date(2026, 11, 20), on_probation=False)

    assert status.ok is True
    assert status.months == []
    assert status.suggestion is None


def test_first_one_day_request_of_a_month_is_within_the_limit():
    status = check(date(2026, 11, 23), date(2026, 11, 23))

    assert status.ok is True
    [november] = status.months
    assert november == MonthUsage(
        month="2026-11", used=Decimal("0"), requested=Decimal("1"), left=Decimal("2"), over=Decimal("0")
    )
