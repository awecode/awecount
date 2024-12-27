from django.core.exceptions import SuspiciousOperation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler


class BadOperation(SuspiciousOperation):
    pass


def exception_handler(exception, context):
    """Handle Django ValidationError as an accepted exception
    Must be set in settings:
    >>> REST_FRAMEWORK = {
    ...     # ...
    ...     'EXCEPTION_HANDLER': 'mtp.apps.common.drf.exception_handler',
    ...     # ...
    ... }
    For the parameters, see ``exception_handler``
    """

    if isinstance(exception, DjangoValidationError):
        detail = None
        if hasattr(exception, "message_dict"):
            detail = exception.message_dict
        elif hasattr(exception, "message"):
            detail = exception.message
        elif hasattr(exception, "messages"):
            detail = exception.messages
        if detail:
            exception = DRFValidationError(detail=detail)
    elif isinstance(exception, BadOperation):
        exception = DRFValidationError(detail=str(exception))

    return drf_exception_handler(exception, context)


class UnprocessableException(APIException):
    status_code = 422
    default_detail = "Request cannot be processed."
    default_code = "unprocessable_request"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = {"detail": detail, "code": code}
