from django.utils import timezone

from leaves.exceptions import LeaveRequestNotFound
from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    return []


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
    raise NotImplementedError
