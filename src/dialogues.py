"""Поиск ответов по датасету dialogues.txt."""

import os
from pathlib import Path

import nltk

from src.config import DIALOGUES_PATH, SAMPLE_DIALOGUES_PATH
from src.nlp import clear_phrase

_dialogues_structured: dict[str, list[list[str]]] | None = None


def _resolve_dialogues_path() -> str | None:
    base = Path(__file__).resolve().parent.parent
    for rel in (DIALOGUES_PATH, SAMPLE_DIALOGUES_PATH):
        path = base / rel
        if path.exists():
            return str(path)
    return None


def _load_dialogues(path: str) -> list[list[str]]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    dialogues_str = content.split("\n\n")
    dialogues = [d.split("\n")[:2] for d in dialogues_str]

    filtered: list[list[str]] = []
    questions: set[str] = set()

    for dialogue in dialogues:
        if len(dialogue) != 2:
            continue
        question, answer = dialogue
        # Формат датасета: строки начинаются с "- "
        if question.startswith("- "):
            question = question[2:]
        if answer.startswith("- "):
            answer = answer[2:]
        question = clear_phrase(question)
        if question and question not in questions:
            questions.add(question)
            filtered.append([question, answer])

    return filtered


def _build_index(dialogues: list[list[str]]) -> dict[str, list[list[str]]]:
    structured: dict[str, list[list[str]]] = {}
    for question, answer in dialogues:
        for word in set(question.split()):
            if len(word) < 2:
                continue
            structured.setdefault(word, []).append([question, answer])

    cut: dict[str, list[list[str]]] = {}
    for word, pairs in structured.items():
        pairs.sort(key=lambda p: len(p[0]))
        cut[word] = pairs[:1000]
    return cut


def init_dialogues() -> bool:
    """Загружает датасет диалогов. Возвращает True, если файл найден."""
    global _dialogues_structured
    path = _resolve_dialogues_path()
    if not path:
        _dialogues_structured = {}
        return False
    dialogues = _load_dialogues(path)
    _dialogues_structured = _build_index(dialogues)
    return True


def generate_answer(replica: str) -> str | None:
    global _dialogues_structured
    if _dialogues_structured is None:
        init_dialogues()
    if not _dialogues_structured:
        return None

    replica = clear_phrase(replica)
    if not replica:
        return None

    words = set(replica.split())
    seen: set[str] = set()
    mini_dataset: list[list[str]] = []

    for word in words:
        pairs = _dialogues_structured.get(word, [])
        for pair in pairs:
            key = pair[0]
            if key not in seen:
                seen.add(key)
                mini_dataset.append(pair)

    answers: list[tuple[float, str, str]] = []
    for question, answer in mini_dataset:
        if not question:
            continue
        len_diff = abs(len(replica) - len(question)) / len(question)
        if len_diff >= 0.2:
            continue
        distance = nltk.edit_distance(replica, question)
        distance_weighted = distance / len(question)
        if distance_weighted < 0.2:
            answers.append((distance_weighted, question, answer))

    if answers:
        return min(answers, key=lambda t: t[0])[2]
    return None
