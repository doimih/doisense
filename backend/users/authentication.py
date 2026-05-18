from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Read JWT from Authorization header first, then fallback to access cookie."""

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            cookie_name = getattr(settings, "JWT_ACCESS_COOKIE_NAME", "doisense_access")
            raw_token = request.COOKIES.get(cookie_name)
            if not raw_token:
                return None

            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token

        return super().authenticate(request)
