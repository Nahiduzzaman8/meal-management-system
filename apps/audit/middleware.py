from __future__ import annotations

import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """Assign a UUID to each incoming request for consistent audit correlation."""

    def process_request(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        try:
            request.request_id = uuid.UUID(request_id)
        except (TypeError, ValueError):
            request.request_id = uuid.uuid4()

        request.META["HTTP_X_REQUEST_ID"] = str(request.request_id)
        request.META["REQUEST_ID"] = str(request.request_id)
        return None
