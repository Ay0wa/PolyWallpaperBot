#!/usr/bin/env python3
"""Консольный режим для тестирования бота без Telegram."""

from src.bot_core import bot, initialize, stats
from src.intents import hist_theme, reset_theme_history
from src.products import reset_ad_counter


def main():
    info = initialize()
    print("=" * 50)
    print("Чат-бот «Политех Обои» — консольный режим")
    print(f"Датасет диалогов: {'загружен' if info['dialogues_loaded'] else 'не найден (используйте data/dialogues.txt)'}")
    print("Введите пустую строку для выхода.")
    print("=" * 50)

    reset_theme_history()
    reset_ad_counter()

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not question:
            break

        answer = bot(question)
        print(f"< {answer}")
        print(f"  [темы: {hist_theme}] [статистика: {stats}]")
        print()


if __name__ == "__main__":
    main()
