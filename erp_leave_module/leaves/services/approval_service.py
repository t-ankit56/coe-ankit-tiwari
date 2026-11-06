from django.utils import timezone

from leaves.exceptions import CommentRequiredToReject, LeaveAlreadyDecided, LeaveRequestNotFound, NotTheAssignedApprover
from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    waiting = LeaveRequest.objects.filter(approver=approver, status=LeaveRequest.Status.PENDING)
    return list(waiting.order_by("start_date", "id"))


def approve_leave(approver, leave_id) -> LeaveRequest:
    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        raise LeaveRequestNotFound()
    if leave.approver_id != approver.id:
        raise NotTheAssignedApprover()
    if leave.status != LeaveRequest.Status.PENDING:
        raise LeaveAlreadyDecided()
    leave.status = LeaveRequest.Status.APPROVED
    leave.decided_at = timezone.now()
    leave.save()
    return leave


def reject_leave(approver, leave_id, comment) -> LeaveRequest:
    leave = LeaveRequest.objects.get(id=leave_id)
    if leave.approver_id != approver.id:
        raise NotTheAssignedApprover()
    if leave.status != LeaveRequest.Status.PENDING:
        raise LeaveAlreadyDecided()
    if not comment.strip():
        raise CommentRequiredToReject()
    leave.status = LeaveRequest.Status.REJECTED
    leave.decision_comment = comment.strip()
    leave.decided_at = timezone.now()
    leave.save()
    return leave
