"""Ядро чат-бота: NLU + генерация ответа."""

import random

from src.config import BOT_CONFIG
from src.dialogues import generate_answer, init_dialogues
from src.intents import classify_intent, hist_theme
from src.nlp import analyze_sentiment, sentiment_label
from src.products import (
    catalog_summary,
    get_price_response,
    get_product_response,
    maybe_inject_ad,
)

stats = {"intent": 0, "generate": 0, "failure": 0, "product": 0}


def get_answer_by_intent(intent: str) -> str | None:
    product_answer = get_product_response(intent)
    if product_answer:
        stats["product"] += 1
        return product_answer

    if intent == "browse_wallpapers":
        return catalog_summary()

    if intent == "ask_price":
        theme = hist_theme[0] if hist_theme else None
        return get_price_response(theme)

    if intent in BOT_CONFIG["intents"]:
        responses = BOT_CONFIG["intents"][intent]["responses"]
        if responses:
            return random.choice(responses)
    return None


def get_failure_phrase() -> str:
    return random.choice(BOT_CONFIG["failure_phrases"])


def bot(replica: str) -> str:
    """
    Основная функция бота.
    replica — фраза пользователя, возвращает ответ.
    """
    intent = classify_intent(replica)

    if intent:
        answer = get_answer_by_intent(intent)
        if answer:
            stats["intent"] += 1
            answer = _enrich_with_sentiment(answer, replica)
            return maybe_inject_ad(answer, intent)

    answer = generate_answer(replica)
    if answer:
        stats["generate"] += 1
        answer = _enrich_with_sentiment(answer, replica)
        return maybe_inject_ad(answer, intent)

    stats["failure"] += 1
    return get_failure_phrase()


def _enrich_with_sentiment(answer: str, replica: str) -> str:
    """Добавляет реакцию на тональность пользователя."""
    score = analyze_sentiment(replica)
    label = sentiment_label(score)
    if label == "negative":
        return f"{answer}\n\nПонимаю ваши сомнения — могу предложить бюджетный вариант «Геометрия Pro» от 1200 ₽."
    if label == "positive":
        return f"{answer}\n\nРада, что вам нравится! Могу помочь с оформлением заказа."
    return answer


def initialize():
    """Инициализация: загрузка датасета диалогов и обучение ML."""
    loaded = init_dialogues()
    return {"dialogues_loaded": loaded, "stats": stats.copy()}
