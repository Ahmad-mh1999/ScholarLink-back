
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is None:
        # Handle exceptions that DRF doesn't handle by default, like IntegrityError
        if isinstance(exc, IntegrityError):
            return Response(
                {"detail": "A database integrity error occurred. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Handle other unexpected errors
        return Response(
            {"detail": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
