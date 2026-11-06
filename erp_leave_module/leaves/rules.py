"""Pure leave rules. No Django, no database, no clock."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Mapping, Sequence

from leaves.exceptions import EndDateIsBeforeStartDate, HalfDayNeedsASingleWorkingDay

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
    if end_date < start_date:
        raise EndDateIsBeforeStartDate()
    if half_day and start_date != end_date:
        raise HalfDayNeedsASingleWorkingDay()
    breakdown = []
    day = start_date
    while day <= end_date:
        if day in holidays:
            breakdown.append(DayInRange(day, Decimal("0"), f"{holidays[day]}, not counted"))
        elif day.weekday() >= 5:
            breakdown.append(DayInRange(day, Decimal("0"), "Weekend"))
        else:
            counts = Decimal("0.5") if half_day else Decimal("1")
            breakdown.append(DayInRange(day, counts, None))
        day += timedelta(days=1)
    if half_day and breakdown[0].counts == 0:
        raise HalfDayNeedsASingleWorkingDay()
    return breakdown


def count_working_days(start_date, end_date, holidays: Holidays, half_day=False) -> Decimal:
    return sum(
        (day.counts for day in explain_each_day(start_date, end_date, holidays, half_day)),
        Decimal("0"),
    )


def find_overlapping_leave(start_date, end_date, existing: Sequence[LeaveRecord]) -> LeaveRecord | None:
    for other in existing:
        if other.status != "rejected" and start_date <= other.end_date and other.start_date <= end_date:
            return other
    return None


def check_probation_limit(*, on_probation: bool, start_date, end_date, half_day: bool,
                          existing: Sequence[LeaveRecord], holidays: Holidays,
                          limit: Decimal = PROBATION_MONTHLY_LIMIT) -> ProbationStatus:
    if not on_probation:
        return ProbationStatus(ok=True, limit=limit, months=[], suggestion=None)
    requested_by_month: dict[str, Decimal] = {}
    for day in explain_each_day(start_date, end_date, holidays, half_day):
        month = day.date.strftime("%Y-%m")
        requested_by_month[month] = requested_by_month.get(month, Decimal("0")) + day.counts
    used_by_month: dict[str, Decimal] = {}
    for record in existing:
        for day in explain_each_day(record.start_date, record.end_date, holidays, record.half_day):
            month = day.date.strftime("%Y-%m")
            used_by_month[month] = used_by_month.get(month, Decimal("0")) + day.counts
    months = [
        MonthUsage(
            month=month,
            used=used_by_month.get(month, Decimal("0")),
            requested=requested,
            left=max(Decimal("0"), limit - used_by_month.get(month, Decimal("0"))),
            over=max(Decimal("0"), used_by_month.get(month, Decimal("0")) + requested - limit),
        )
        for month, requested in requested_by_month.items()
    ]
    return ProbationStatus(ok=all(month.over == 0 for month in months), limit=limit, months=months, suggestion=None)


def suggest_largest_fitting_request(*, start_date, end_date, existing, holidays,
                                    limit=PROBATION_MONTHLY_LIMIT) -> SuggestedRequest | None:
    raise NotImplementedError
