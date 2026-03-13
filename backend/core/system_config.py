from django.conf import settings
from django.core.cache import cache

from .models import SystemConfig


_CACHE_KEY = "core:system_config"
_CACHE_TIMEOUT = 60


def get_system_config() -> SystemConfig:
    config = cache.get(_CACHE_KEY)
    if config is None:
        config = SystemConfig.get_solo()
        cache.set(_CACHE_KEY, config, _CACHE_TIMEOUT)
    return config


def get_google_client_id() -> str:
    config = get_system_config()
    return (config.google_client_id or settings.GOOGLE_CLIENT_ID or "").strip()


def get_apple_client_id() -> str:
    config = get_system_config()
    return (config.apple_client_id or settings.APPLE_CLIENT_ID or "").strip()


def get_ai_chat_rate_limit() -> int:
    config = get_system_config()
    return config.ai_chat_rate_limit or getattr(settings, "AI_CHAT_RATE_LIMIT", 20)


def get_stripe_secret_key() -> str:
    config = get_system_config()
    return (config.stripe_secret_key or settings.STRIPE_SECRET_KEY or "").strip()


def get_stripe_webhook_secret() -> str:
    config = get_system_config()
    return (config.stripe_webhook_secret or settings.STRIPE_WEBHOOK_SECRET or "").strip()


def get_stripe_price_id_premium() -> str:
    config = get_system_config()
    return (config.stripe_price_id_premium or settings.STRIPE_PRICE_ID_PREMIUM or "").strip()


def get_stripe_price_id_basic() -> str:
    config = get_system_config()
    return (config.stripe_price_id_basic or getattr(settings, "STRIPE_PRICE_ID_BASIC", "") or "").strip()


def get_stripe_price_id_vip() -> str:
    config = get_system_config()
    return (config.stripe_price_id_vip or getattr(settings, "STRIPE_PRICE_ID_VIP", "") or "").strip()


def get_stripe_product_id_basic() -> str:
    config = get_system_config()
    return (config.stripe_product_id_basic or getattr(settings, "STRIPE_PRODUCT_ID_BASIC", "") or "").strip()


def get_stripe_product_id_premium() -> str:
    config = get_system_config()
    return (config.stripe_product_id_premium or getattr(settings, "STRIPE_PRODUCT_ID_PREMIUM", "") or "").strip()


def get_stripe_product_id_vip() -> str:
    config = get_system_config()
    return (config.stripe_product_id_vip or getattr(settings, "STRIPE_PRODUCT_ID_VIP", "") or "").strip()


def get_stripe_price_id_for_tier(plan_tier: str) -> str:
    mapping = {
        "basic": get_stripe_price_id_basic,
        "premium": get_stripe_price_id_premium,
        "vip": get_stripe_price_id_vip,
    }
    getter = mapping.get(plan_tier, get_stripe_price_id_premium)
    return getter()


def get_stripe_product_id_for_tier(plan_tier: str) -> str:
    mapping = {
        "basic": get_stripe_product_id_basic,
        "premium": get_stripe_product_id_premium,
        "vip": get_stripe_product_id_vip,
    }
    getter = mapping.get(plan_tier, get_stripe_product_id_premium)
    return getter()


def plan_tier_from_stripe_price_id(price_id: str) -> str:
    """Reverse-map a Stripe price ID to an internal plan tier."""
    if price_id and price_id == get_stripe_price_id_basic():
        return "basic"
    if price_id and price_id == get_stripe_price_id_vip():
        return "vip"
    if price_id and price_id == get_stripe_price_id_premium():
        return "premium"
    return "premium"  # Default fallback


def plan_tier_from_stripe_product_id(product_id: str) -> str:
    """Reverse-map a Stripe product ID to an internal plan tier."""
    if product_id and product_id == get_stripe_product_id_basic():
        return "basic"
    if product_id and product_id == get_stripe_product_id_vip():
        return "vip"
    if product_id and product_id == get_stripe_product_id_premium():
        return "premium"
    return "premium"  # Default fallback


def get_enabled_languages() -> list[str]:
    config = get_system_config()
    langs = config.enabled_languages or []
    if langs:
        return langs
    return list(getattr(settings, "SUPPORTED_LANGUAGES", ["ro", "en"]))


def get_default_site_language() -> str:
    config = get_system_config()
    value = (config.default_site_language or "").strip()
    return value or "ro"


def get_ai_temperature() -> float:
    config = get_system_config()
    return float(config.ai_temperature or 0.7)


def get_ai_max_tokens() -> int:
    config = get_system_config()
    return int(config.ai_max_tokens or 1024)


def get_ai_request_timeout_seconds() -> int:
    config = get_system_config()
    return int(config.ai_request_timeout_seconds or 45)
