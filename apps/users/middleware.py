from __future__ import annotations

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

ALLOWED_WHEN_PASSWORD_CHANGE_REQUIRED = {
    "/api/auth/me/",
    "/api/auth/password/change/",
    "/api/auth/logout/",
}


class MustChangePasswordMiddleware(MiddlewareMixin):
    """Block access to all endpoints while the user must change their password."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return None

        if not request.user.must_change_password:
            return None

        if request.path in ALLOWED_WHEN_PASSWORD_CHANGE_REQUIRED:
            return None

        return JsonResponse(
            {
                "code": "password_change_required",
                "message": "You must change your password before accessing this endpoint.",
            },
            status=403,
        )
