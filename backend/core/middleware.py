import ipaddress

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .system_config import get_qa_allowed_source_ips

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

        component = (
            "api" if path.startswith("/api/") else "admin" if "/admin/" in path else "backend"
        )
        user = (
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else None
        )

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


class QAIPAllowlistMiddleware(MiddlewareMixin):
    """Restrict API access to configured source IPs/CIDRs for QA environments."""

    _EXEMPT_PATHS = {
        "/api/health",
        "/api/health/",
    }

    def _client_ip(self, request) -> str:
        xff = (request.META.get("HTTP_X_FORWARDED_FOR", "") or "").strip()
        if xff:
            # Left-most IP is the original client according to X-Forwarded-For convention.
            return xff.split(",")[0].strip()

        x_real_ip = (request.META.get("HTTP_X_REAL_IP", "") or "").strip()
        if x_real_ip:
            return x_real_ip

        return (request.META.get("REMOTE_ADDR", "") or "").strip()

    def _is_allowed(self, client_ip: str, allowed_entries: list[str]) -> bool:
        try:
            ip_obj = ipaddress.ip_address(client_ip)
        except ValueError:
            return False

        for raw in allowed_entries:
            try:
                net = ipaddress.ip_network(raw, strict=False)
            except ValueError:
                continue
            if ip_obj in net:
                return True

        return False

    def process_request(self, request):
        path = request.path or ""
        if not path.startswith("/api/"):
            return None

        if path in self._EXEMPT_PATHS:
            return None

        allowed_entries = get_qa_allowed_source_ips()
        if not allowed_entries:
            return None

        client_ip = self._client_ip(request)
        if self._is_allowed(client_ip, allowed_entries):
            return None

        return JsonResponse(
            {
                "detail": "Forbidden: source IP is not allowlisted.",
                "code": "ip_not_allowed",
            },
            status=403,
        )
