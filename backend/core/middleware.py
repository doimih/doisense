from django.utils.deprecation import MiddlewareMixin

from .models import SystemErrorEvent


class SystemErrorLoggingMiddleware(MiddlewareMixin):
    """Capture unhandled backend exceptions into a centralized admin-visible log."""

    _SKIP_PREFIXES = (
        "/doisense/ro/admin/static/",
        "/doisense/media/",
        "/favicon.ico",
    )

    def process_exception(self, request, exception):
        path = (request.path or "")[:255]
        if any(path.startswith(prefix) for prefix in self._SKIP_PREFIXES):
            return None

        component = "api" if path.startswith("/api/") else "admin" if "/admin/" in path else "backend"
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

        query = request.GET.dict() if hasattr(request, "GET") else {}
        context = {
            "query": {k: str(v)[:200] for k, v in list(query.items())[:20]},
            "user_agent": (request.META.get("HTTP_USER_AGENT", "") or "")[:255],
            "remote_addr": (request.META.get("REMOTE_ADDR", "") or "")[:64],
        }

        try:
            SystemErrorEvent.objects.create(
                user=user,
                severity=SystemErrorEvent.SEVERITY_CRITICAL,
                component=component,
                endpoint=path,
                http_method=(request.method or "")[:12],
                status_code=500,
                error_type=exception.__class__.__name__[:128],
                message=str(exception)[:2000],
                context=context,
            )
        except Exception:
            # Never block request exception handling because of logging persistence errors.
            return None

        return None
