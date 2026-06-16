"""Классификация намерений: ML (sklearn) + расстояние Левенштейна + темы."""

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from src.config import BOT_CONFIG, HIST_THEME_LEN
from src.nlp import clear_phrase


class IntentClassifier:
    """Обучаемый классификатор намерений на TfidfVectorizer + LinearSVC."""

    def __init__(self):
        self._vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 3))
        self._clf = LinearSVC()
        self._train()

    def _train(self):
        x_text = []
        y = []
        for intent, data in BOT_CONFIG["intents"].items():
            for example in data["examples"]:
                x_text.append(clear_phrase(example))
                y.append(intent)
        x = self._vectorizer.fit_transform(x_text)
        self._clf.fit(x, y)

    def predict(self, replica: str) -> str | None:
        replica = clear_phrase(replica)
        if not replica:
            return None

        intent = self._clf.predict(self._vectorizer.transform([replica]))[0]

        for example in BOT_CONFIG["intents"][intent]["examples"]:
            example = clear_phrase(example)
            if not example:
                continue
            distance = nltk.edit_distance(replica, example)
            if distance / len(example) <= 0.5:
                return intent
        return None


_classifier: IntentClassifier | None = None
hist_theme: list[str] = []


def get_classifier() -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def reset_theme_history():
    hist_theme.clear()


def classify_intent_by_theme(replica: str, theme: str | None = None) -> str | None:
    clf = get_classifier()
    replica_clean = clear_phrase(replica)
    if not replica_clean:
        return None

    predicted = clf.predict(replica_clean)
    if predicted is None:
        return None

    intent_data = BOT_CONFIG["intents"].get(predicted, {})
    theme_app = intent_data.get("theme_app")

    if theme_app is not None:
        if theme not in theme_app and "*" not in theme_app:
            return None
    elif theme is not None:
        return None

    return predicted


def classify_intent(replica: str) -> str | None:
    lev = 0
    intent = None

    for theme in hist_theme:
        intent = classify_intent_by_theme(replica, theme)
        if intent is not None:
            break
        lev += 1

    if intent is None:
        lev = 0
        intent = classify_intent_by_theme(replica)
    elif lev > 0:
        del hist_theme[:lev]

    if intent is not None:
        theme_gen = BOT_CONFIG["intents"][intent].get("theme_gen")
        if theme_gen and theme_gen not in hist_theme:
            hist_theme.insert(0, theme_gen)
            if len(hist_theme) > HIST_THEME_LEN:
                hist_theme.pop()

    return intent
