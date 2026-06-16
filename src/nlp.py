"""Обработка естественного языка: очистка, тональность."""

import re

# Простой словарь тональности (фрагмент для демонстрации)
SENTIMENT_WORDS = {
    "люблю": 1.0,
    "нравится": 0.8,
    "отлично": 0.9,
    "класс": 0.7,
    "супер": 0.9,
    "хорошо": 0.5,
    "плохо": -0.6,
    "ужас": -0.9,
    "ненавижу": -1.0,
    "дорого": -0.4,
    "дешево": 0.3,
    "красиво": 0.7,
    "некрасиво": -0.7,
}


def clear_phrase(phrase: str) -> str:
    """Очистка ввода: нижний регистр, только кириллица, пробелы и дефис."""
    if not phrase:
        return ""

    phrase = phrase.lower().strip()
    # Схлопываем множественные пробелы
    phrase = re.sub(r"\s+", " ", phrase)
    # Удаляем повторяющиеся знаки препинания
    phrase = re.sub(r"([!?.,])\1+", r"\1", phrase)

    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя- "
    result = "".join(symbol for symbol in phrase if symbol in alphabet)
    return result.strip()


def analyze_sentiment(phrase: str) -> float:
    """
    Анализ тональности по словарю.
    Возвращает значение от -1 (негатив) до +1 (позитив).
    """
    words = clear_phrase(phrase).split()
    if not words:
        return 0.0

    scores = [SENTIMENT_WORDS[w] for w in words if w in SENTIMENT_WORDS]
    if not scores:
        return 0.0
    return max(-1.0, min(1.0, sum(scores) / len(scores)))


def sentiment_label(score: float) -> str:
    if score > 0.2:
        return "positive"
    if score < -0.2:
        return "negative"
    return "neutral"
