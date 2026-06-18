"""Поиск ответов по датасету dialogues.txt (индекс в SQLite — мало RAM)."""

import sqlite3
from pathlib import Path

import nltk

from src.config import DIALOGUES_DB_PATH, DIALOGUES_PATH, SAMPLE_DIALOGUES_PATH
from src.nlp import clear_phrase

_db_conn: sqlite3.Connection | None = None
MAX_PAIRS_PER_WORD = 1000


def _base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _resolve_dialogues_path() -> Path | None:
    for rel in (DIALOGUES_PATH, SAMPLE_DIALOGUES_PATH):
        path = _base_dir() / rel
        if path.exists():
            return path
    return None


def _db_path() -> Path:
    return _base_dir() / DIALOGUES_DB_PATH


def _strip_replica(line: str) -> str:
    if line.startswith("- "):
        return line[2:]
    return line


def _iter_pairs(path: Path):
    """Потоковое чтение пар вопрос-ответ без загрузки всего файла в память."""
    questions: set[str] = set()
    block: list[str] = []

    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                if len(block) >= 2:
                    question = clear_phrase(_strip_replica(block[0]))
                    answer = _strip_replica(block[1])
                    if question and question not in questions:
                        questions.add(question)
                        yield question, answer
                block = []
                continue
            if len(block) < 2:
                block.append(line)

        if len(block) >= 2:
            question = clear_phrase(_strip_replica(block[0]))
            answer = _strip_replica(block[1])
            if question and question not in questions:
                yield question, answer


def _build_index(txt_path: Path, db_path: Path) -> None:
    """Строит SQLite-индекс потоково (как в методичке: до 1000 пар на слово)."""
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE word_index (word TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL)"
    )
    conn.execute("CREATE INDEX idx_word ON word_index(word)")

    word_counts: dict[str, int] = {}
    batch: list[tuple[str, str, str]] = []
    batch_size = 5000

    for question, answer in _iter_pairs(txt_path):
        for word in set(question.split()):
            if len(word) < 2:
                continue
            count = word_counts.get(word, 0)
            if count >= MAX_PAIRS_PER_WORD:
                continue
            batch.append((word, question, answer))
            word_counts[word] = count + 1
            if len(batch) >= batch_size:
                conn.executemany("INSERT INTO word_index VALUES (?, ?, ?)", batch)
                batch.clear()

    if batch:
        conn.executemany("INSERT INTO word_index VALUES (?, ?, ?)", batch)
    conn.commit()
    conn.close()


def init_dialogues() -> bool:
    """Загружает или строит SQLite-индекс. Возвращает True, если датасет найден."""
    global _db_conn

    txt_path = _resolve_dialogues_path()
    if txt_path is None:
        return False

    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists() or db_path.stat().st_mtime < txt_path.stat().st_mtime:
        _build_index(txt_path, db_path)

    _db_conn = sqlite3.connect(db_path, check_same_thread=False)
    _db_conn.execute("PRAGMA query_only=ON")
    return True


def _get_conn() -> sqlite3.Connection | None:
    global _db_conn
    if _db_conn is None and not init_dialogues():
        return None
    return _db_conn


def generate_answer(replica: str) -> str | None:
    conn = _get_conn()
    if conn is None:
        return None

    replica = clear_phrase(replica)
    if not replica:
        return None

    seen: set[str] = set()
    mini_dataset: list[tuple[str, str]] = []

    for word in set(replica.split()):
        if len(word) < 2:
            continue
        for question, answer in conn.execute(
            "SELECT question, answer FROM word_index WHERE word = ?", (word,)
        ):
            if question not in seen:
                seen.add(question)
                mini_dataset.append((question, answer))

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
