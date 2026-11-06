from django.utils import timezone

from leaves.exceptions import LeaveRequestNotFound
from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    waiting = LeaveRequest.objects.filter(approver=approver, status=LeaveRequest.Status.PENDING)
    return list(waiting.order_by("start_date", "id"))


def approve_leave(approver, leave_id) -> LeaveRequest:
    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        raise LeaveRequestNotFound()
    leave.status = LeaveRequest.Status.APPROVED
    leave.decided_at = timezone.now()
    leave.save()
    return leave


def reject_leave(approver, leave_id, comment) -> LeaveRequest:
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = LeaveRequest.Status.REJECTED
    leave.decision_comment = comment
    leave.decided_at = timezone.now()
    leave.save()
    return leave
