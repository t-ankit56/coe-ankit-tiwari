from leaves.models import Holiday, LeaveRequest
from leaves.rules import Holidays, LeaveRecord


def to_leave_record(leave_request: LeaveRequest) -> LeaveRecord:
    return LeaveRecord(
        id=leave_request.id,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        half_day=leave_request.half_day,
        status=leave_request.status,
    )


def load_holidays() -> Holidays:
    return {holiday.date: holiday.name for holiday in Holiday.objects.all()}
