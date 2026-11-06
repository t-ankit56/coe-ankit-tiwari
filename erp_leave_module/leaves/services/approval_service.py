from leaves.models import LeaveRequest


def list_waiting_approvals(approver) -> list[LeaveRequest]:
    raise NotImplementedError


def approve_leave(approver, leave_id) -> LeaveRequest:
    raise NotImplementedError


def reject_leave(approver, leave_id, comment) -> LeaveRequest:
    raise NotImplementedError
