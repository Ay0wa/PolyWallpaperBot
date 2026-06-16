"""Каталог обоев и сценарии рекламы."""

import random

from src.config import PRODUCTS


def format_product(product_key: str) -> str:
    p = PRODUCTS[product_key]
    colors = ", ".join(p["colors"])
    return (
        f"📋 *{p['name']}*\n"
        f"Материал: {p['material']}\n"
        f"Цена: {p['price']} ₽/рулон\n"
        f"Размер: {p['width_cm']} см × {p['length_m']} м\n"
        f"Цвета: {colors}\n"
        f"{p['description']}"
    )


def catalog_summary() -> str:
    lines = ["🎨 *Наш каталог обоев:*\n"]
    for key in PRODUCTS:
        p = PRODUCTS[key]
        lines.append(f"• *{p['name']}* — {p['price']} ₽ ({p['material']})")
    lines.append("\nНапишите название коллекции, чтобы узнать подробности.")
    return "\n".join(lines)


def get_product_response(intent: str) -> str | None:
    if intent in PRODUCTS:
        return format_product(intent)
    return None


def get_price_response(theme: str | None) -> str:
    if theme and theme in PRODUCTS:
        p = PRODUCTS[theme]
        return f"Коллекция «{p['name']}» стоит {p['price']} ₽ за рулон."
    return catalog_summary()


# Сценарии плавного перевода на рекламу (по счётчику сообщений)
AD_SCENARIOS = [
    "Кстати, если планируете обновить стены — у нас как раз новая коллекция «Лесная сказка»!",
    "А вы уже думали об обоях? Сейчас отличные цены на «Парижские мотивы».",
    "Между прочим, влагостойкие «Геометрия Pro» идеально подходят для любой комнаты.",
    "Если интересует ремонт — могу подобрать обои под ваш интерьер. Это бесплатно!",
]

_msg_counter = 0


def maybe_inject_ad(answer: str, intent: str | None) -> str:
    """Ненавязчиво добавляет рекламу после нескольких сообщений без покупки."""
    global _msg_counter
    _msg_counter += 1

    skip_intents = {"hello", "bye", "name", "help", "want_buy", "delivery"}
    product_intents = set(PRODUCTS.keys()) | {"browse_wallpapers", "renovation"}

    if intent in skip_intents or intent in product_intents:
        return answer

    # Каждые 4 сообщения — мягкая реклама
    if _msg_counter % 4 == 0:
        ad = random.choice(AD_SCENARIOS)
        return f"{answer}\n\n💡 {ad}"
    return answer


def reset_ad_counter():
    global _msg_counter
    _msg_counter = 0
