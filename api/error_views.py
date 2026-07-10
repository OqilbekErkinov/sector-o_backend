from django.http import JsonResponse
from django.views import defaults as django_default_views

# Registered as handler404/handler500 in ironpulse_backend/urls.py. Django
# only reaches these when DEBUG=False (with DEBUG=True it always shows its
# own technical debug page instead, regardless of these handlers) — that's
# exactly the production case where an unmatched /api/ URL, or an exception
# raised outside DRF's own dispatch/exception_handler cycle (e.g. in
# landing_view or middleware), would otherwise return Django's plain HTML
# error page instead of the JSON the frontend's $fetch expects.


def api_404(request, exception=None):
    if request.path.startswith('/api/'):
        return JsonResponse({'error': 'Not found'}, status=404)
    return django_default_views.page_not_found(request, exception)


def api_500(request):
    if request.path.startswith('/api/'):
        return JsonResponse({'error': 'Internal server error'}, status=500)
    return django_default_views.server_error(request)
