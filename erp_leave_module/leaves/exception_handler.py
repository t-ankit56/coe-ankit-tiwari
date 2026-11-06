from rest_framework.views import exception_handler as drf_default_exception_handler


def translate_leave_errors_to_http(exception, context):
    return drf_default_exception_handler(exception, context)
