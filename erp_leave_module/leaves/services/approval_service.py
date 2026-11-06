from leaves.exceptions import LeaveRequestNotFound
from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    return []


def approve_leave(approver, leave_id) -> LeaveRequest:
    raise LeaveRequestNotFound()


def reject_leave(approver, leave_id, comment) -> LeaveRequest:
    raise NotImplementedError
