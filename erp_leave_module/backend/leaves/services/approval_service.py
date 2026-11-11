from django.utils import timezone

from leaves.exceptions import (
    CommentRequiredToReject,
    LeaveAlreadyDecided,
    LeaveRequestNotFound,
    NotTheAssignedApprover,
)
from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    waiting = LeaveRequest.objects.filter(approver=approver, status=LeaveRequest.Status.PENDING)
    return list(waiting.order_by("start_date", "id"))


def _load_leave_the_approver_may_decide(approver, leave_id) -> LeaveRequest:
    """Checks, in order: it exists, it is assigned to this approver, it is still pending."""
    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        raise LeaveRequestNotFound()
    if leave.approver_id != approver.id:
        raise NotTheAssignedApprover()
    if leave.status != LeaveRequest.Status.PENDING:
        raise LeaveAlreadyDecided()
    return leave


def _record_decision(leave: LeaveRequest, status: str, comment: str = "") -> LeaveRequest:
    leave.status = status
    leave.decision_comment = comment
    leave.decided_at = timezone.now()
    leave.save()
    return leave


def approve_leave(approver, leave_id) -> LeaveRequest:
    leave = _load_leave_the_approver_may_decide(approver, leave_id)
    return _record_decision(leave, LeaveRequest.Status.APPROVED)


def reject_leave(approver, leave_id, comment) -> LeaveRequest:
    leave = _load_leave_the_approver_may_decide(approver, leave_id)
    if not comment.strip():
        raise CommentRequiredToReject()
    return _record_decision(leave, LeaveRequest.Status.REJECTED, comment.strip())
