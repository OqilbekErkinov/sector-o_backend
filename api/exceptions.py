import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .telegram_utils import send_telegram_message

logger = logging.getLogger(__name__)


def _first_error_message(data):
    """Flattens DRF's default error shape — a (possibly nested) dict/list of
    field -> messages, or {'detail': ...} — into one human-readable string,
    matching the `{'error': '...'}` convention the frontend's `err.data?.error`
    already relies on for every hand-written `Response({'error': ...})` call."""
    if isinstance(data, dict):
        for value in data.values():
            message = _first_error_message(value)
            if message:
                return message
        return None
    if isinstance(data, list):
        for item in data:
            message = _first_error_message(item)
            if message:
                return message
        return None
    return str(data)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        # A recognized DRF/API exception (ValidationError, NotAuthenticated,
        # PermissionDenied, NotFound, Throttled, ...). Normalize its shape so
        # every endpoint's failure looks the same to the frontend.
        if not (isinstance(response.data, dict) and 'error' in response.data):
            response.data = {'error': _first_error_message(response.data) or 'Xatolik yuz berdi'}
        return response

    # Anything else is a genuine bug (DB down, unexpected None, third-party
    # API crash, ...) that DRF doesn't recognize and would otherwise surface
    # as Django's HTML debug page (DEBUG=True) or a bare empty 500
    # (DEBUG=False) — neither of which the frontend's $fetch can parse as JSON.
    request = context.get('request')
    method = getattr(request, 'method', '?')
    path = getattr(request, 'path', '?')
    logger.exception("Unhandled exception in %s %s", method, path)
    send_telegram_message(
        f"🔥 Server xatoligi!\n\n"
        f"📍 {method} {path}\n"
        f"⚠️ {exc.__class__.__name__}: {exc}"
    )
    return Response(
        {'error': "Serverda kutilmagan xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
