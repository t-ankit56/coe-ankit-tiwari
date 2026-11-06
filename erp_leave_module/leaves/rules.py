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


def _counted_days_by_month(start_date, end_date, holidays: Holidays, half_day=False) -> dict[str, Decimal]:
    """Counted days per "YYYY-MM". Months the range touches appear even if they count 0."""
    counted: dict[str, Decimal] = {}
    for day in explain_each_day(start_date, end_date, holidays, half_day):
        month = day.date.strftime("%Y-%m")
        counted[month] = counted.get(month, Decimal("0")) + day.counts
    return counted


def _used_days_by_month(existing: Sequence[LeaveRecord], holidays: Holidays) -> dict[str, Decimal]:
    """Days already pending or approved per month. Rejected leave does not count."""
    used: dict[str, Decimal] = {}
    for record in existing:
        if record.status == "rejected":
            continue
        for month, days in _counted_days_by_month(
            record.start_date, record.end_date, holidays, record.half_day
        ).items():
            used[month] = used.get(month, Decimal("0")) + days
    return used


def _month_usage(*, start_date, end_date, half_day, existing, holidays, limit) -> list[MonthUsage]:
    used_by_month = _used_days_by_month(existing, holidays)
    months = []
    for month, requested in _counted_days_by_month(start_date, end_date, holidays, half_day).items():
        used = used_by_month.get(month, Decimal("0"))
        months.append(
            MonthUsage(
                month=month,
                used=used,
                requested=requested,
                left=max(Decimal("0"), limit - used),
                over=max(Decimal("0"), used + requested - limit),
            )
        )
    return months


def check_probation_limit(*, on_probation: bool, start_date, end_date, half_day: bool,
                          existing: Sequence[LeaveRecord], holidays: Holidays,
                          limit: Decimal = PROBATION_MONTHLY_LIMIT) -> ProbationStatus:
    if not on_probation:
        return ProbationStatus(ok=True, limit=limit, months=[], suggestion=None)
    months = _month_usage(
        start_date=start_date, end_date=end_date, half_day=half_day,
        existing=existing, holidays=holidays, limit=limit,
    )
    return ProbationStatus(ok=all(month.over == 0 for month in months), limit=limit, months=months, suggestion=None)


def suggest_largest_fitting_request(*, start_date, end_date, existing, holidays,
                                    limit=PROBATION_MONTHLY_LIMIT) -> SuggestedRequest | None:
    raise NotImplementedError
