from django.conf import settings
from django.core.exceptions import ValidationError


def validate_language(value):
    if value not in settings.SUPPORTED_LANGUAGES:
        raise ValidationError(
            f"Language must be one of: {', '.join(settings.SUPPORTED_LANGUAGES)}"
        )
