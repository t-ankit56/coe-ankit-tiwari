from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone

from leaves.models import LeaveRequest
from leaves.exceptions import LeaveOverlapsExistingLeave, NoApproverAssigned
from leaves.rules import DayInRange, LeaveRecord, ProbationStatus, explain_each_day, find_overlapping_leave
from leaves.services._records import load_holidays, to_leave_record


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
    breakdown = explain_each_day(start_date, end_date, load_holidays(), half_day)
    days = sum((day.counts for day in breakdown), Decimal("0"))
    existing = [to_leave_record(leave) for leave in LeaveRequest.objects.filter(user=user)]
    overlap = find_overlapping_leave(start_date, end_date, existing)
    return LeavePreview(days=days, breakdown=breakdown, overlap=overlap, probation=None)


def submit_leave(user, start_date, end_date, half_day, reason) -> LeaveRequest:
    if user.profile.approver is None:
        raise NoApproverAssigned()
    breakdown = explain_each_day(start_date, end_date, load_holidays(), half_day)
    existing = [to_leave_record(leave) for leave in LeaveRequest.objects.filter(user=user)]
    clashing = find_overlapping_leave(start_date, end_date, existing)
    if clashing:
        raise LeaveOverlapsExistingLeave(clashing)
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
