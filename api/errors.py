from rest_framework.exceptions import ValidationError as InvalidRequest
from rest_framework.response import Response
from rest_framework.views import exception_handler

from domain.errors import Conflict, DomainError, NotFound, ValidationError

STATUS_FOR = ((NotFound, 404), (Conflict, 409), (ValidationError, 400))


def status_for(error: DomainError):
    for error_type, code in STATUS_FOR:
        if isinstance(error, error_type):
            return code
    return 400


def handle_errors(exc, context):
    if isinstance(exc, DomainError):
        return Response({'error': str(exc)}, status=status_for(exc))

    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(exc, InvalidRequest):
        response.data = {'error': 'invalid request', 'details': exc.detail}
    else:
        response.data = {'error': str(response.data['detail'])}
    return response