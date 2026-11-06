from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone

from leaves.models import LeaveRequest
from leaves.rules import DayInRange, LeaveRecord, ProbationStatus, explain_each_day
from leaves.services._records import load_holidays


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
    breakdown = explain_each_day(start_date, end_date, load_holidays(), half_day)
    return LeaveRequest.objects.create(
        user=user,
        approver=user.profile.approver,
        start_date=start_date,
        end_date=end_date,
        half_day=half_day,
        days=sum((day.counts for day in breakdown), Decimal("0")),
        reason=reason,
        status=LeaveRequest.Status.PENDING,
    )


def list_my_leaves(user, today: date | None = None) -> MyLeaves:
    leaves = list(LeaveRequest.objects.filter(user=user).order_by("-created_at", "-id"))
    today = today or timezone.localdate()
    days_taken = sum(
        (
            leave.days
            for leave in leaves
            if leave.status == LeaveRequest.Status.APPROVED and leave.start_date.year == today.year
        ),
        Decimal("0"),
    )
    pending_count = sum(1 for leave in leaves if leave.status == LeaveRequest.Status.PENDING)
    return MyLeaves(days_taken=days_taken, pending_count=pending_count, leaves=leaves)
