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


def test_existing_leave_in_the_same_month_counts_towards_the_limit():
    status = check(date(2026, 11, 23), date(2026, 11, 23), existing=[approved(date(2026, 11, 2), date(2026, 11, 2))])

    assert status.ok is True
    [november] = status.months
    assert (november.used, november.requested, november.left) == (Decimal("1"), Decimal("1"), Decimal("1"))


def test_two_day_request_with_one_and_a_half_days_used_is_over_by_one_and_a_half():
    status = check(date(2026, 11, 19), date(2026, 11, 20), existing=AARAV_USED)

    assert status.ok is False
    [november] = status.months
    assert (november.used, november.requested, november.left, november.over) == (
        Decimal("1.5"), Decimal("2"), Decimal("0.5"), Decimal("1.5")
    )


def test_request_that_exactly_reaches_the_limit_is_allowed():
    status = check(date(2026, 11, 19), date(2026, 11, 19), existing=AARAV_USED, half_day=True)

    assert status.ok is True
    [november] = status.months
    assert november.over == Decimal("0")
    assert november.left == Decimal("0.5")
    assert november.used + november.requested == status.limit


def test_one_day_request_with_one_and_a_half_days_used_is_over_by_half_a_day():
    status = check(date(2026, 11, 19), date(2026, 11, 19), existing=AARAV_USED)

    assert status.ok is False
    assert status.months[0].over == Decimal("0.5")
