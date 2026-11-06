from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from leaves.models import LeaveRequest
from leaves.rules import DayInRange, LeaveRecord, ProbationStatus


@dataclass
class LeavePreview:
    days: Decimal
    breakdown: list[DayInRange]
    overlap: LeaveRecord | None
    probation: ProbationStatus | None


@dataclass
class MyLeaves:
    days_taken: Decimal
    pending_count: int
    leaves: list[LeaveRequest]


def preview_leave(user, start_date, end_date, half_day=False) -> LeavePreview:
    raise NotImplementedError


def submit_leave(user, start_date, end_date, half_day, reason) -> LeaveRequest:
    raise NotImplementedError


def list_my_leaves(user, today: date | None = None) -> MyLeaves:
    return MyLeaves(days_taken=Decimal("0"), pending_count=0, leaves=[])
