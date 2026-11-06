"""Pure leave rules. No Django, no database, no clock."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Mapping, Sequence

Holidays = Mapping[date, str]  # date -> holiday name


@dataclass(frozen=True)
class DayInRange:
    date: date
    counts: Decimal  # Decimal("1"), Decimal("0.5") or Decimal("0")
    label: str | None  # None, "Weekend", or "<Holiday name>, not counted"


@dataclass(frozen=True)
class LeaveRecord:
    id: int | None
    start_date: date
    end_date: date
    half_day: bool
    status: str  # "pending" | "approved" | "rejected"


@dataclass(frozen=True)
class SuggestedRequest:
    start_date: date
    end_date: date
    half_day: bool


@dataclass(frozen=True)
class MonthUsage:
    month: str  # "2026-11"
    used: Decimal
    requested: Decimal
    left: Decimal
    over: Decimal


@dataclass(frozen=True)
class ProbationStatus:
    ok: bool
    limit: Decimal
    months: list[MonthUsage]
    suggestion: SuggestedRequest | None


PROBATION_MONTHLY_LIMIT = Decimal("2")


def explain_each_day(start_date, end_date, holidays: Holidays, half_day=False) -> list[DayInRange]:
    raise NotImplementedError


def count_working_days(start_date, end_date, holidays: Holidays, half_day=False) -> Decimal:
    if half_day:
        return Decimal("0.5")
    total = Decimal("0")
    day = start_date
    while day <= end_date:
        if day.weekday() < 5 and day not in holidays:
            total += 1
        day += timedelta(days=1)
    return total


def find_overlapping_leave(start_date, end_date, existing: Sequence[LeaveRecord]) -> LeaveRecord | None:
    raise NotImplementedError


def check_probation_limit(*, on_probation: bool, start_date, end_date, half_day: bool,
                          existing: Sequence[LeaveRecord], holidays: Holidays,
                          limit: Decimal = PROBATION_MONTHLY_LIMIT) -> ProbationStatus:
    raise NotImplementedError


def suggest_largest_fitting_request(*, start_date, end_date, existing, holidays,
                                    limit=PROBATION_MONTHLY_LIMIT) -> SuggestedRequest | None:
    raise NotImplementedError
