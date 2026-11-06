from rest_framework.exceptions import ValidationError

from leaves.exceptions import (
    EndDateIsBeforeStartDate,
    HalfDayNeedsASingleWorkingDay,
    LeaveError,
    LeaveOverlapsExistingLeave,
    LeaveRequestNotFound,
    NoApproverAssigned,
    ProbationLimitExceeded,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler


HTTP_STATUS_FOR_LEAVE_ERROR = {
    EndDateIsBeforeStartDate: 400,
    HalfDayNeedsASingleWorkingDay: 400,
    LeaveOverlapsExistingLeave: 400,
    ProbationLimitExceeded: 400,
    NoApproverAssigned: 400,
    LeaveRequestNotFound: 404,
}


def _first_message(detail) -> str:
    """Flatten DRF validation detail into one readable message."""
    if isinstance(detail, dict):
        field, messages = next(iter(detail.items()))
        message = _first_message(messages)
        return message if field == "non_field_errors" else f"{field}: {message}"
    if isinstance(detail, list):
        return _first_message(detail[0])
    return str(detail)


def translate_leave_errors_to_http(exception, context):
    if isinstance(exception, ValidationError):
        return Response({"error": _first_message(exception.detail)}, status=400)
    if isinstance(exception, LeaveError):
        status = HTTP_STATUS_FOR_LEAVE_ERROR[type(exception)]
        return Response({"error": str(exception)}, status=status)
    return drf_default_exception_handler(exception, context)
