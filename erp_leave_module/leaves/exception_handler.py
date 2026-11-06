from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler


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
    return drf_default_exception_handler(exception, context)
