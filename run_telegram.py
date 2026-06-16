"""Запуск бота в Telegram."""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.bot_core import bot, initialize, stats
from src.intents import reset_theme_history
from src.products import catalog_summary, reset_ad_counter

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_theme_history()
    reset_ad_counter()
    await update.message.reply_text(
        "Здравствуйте! Я консультант магазина обоев «Политех».\n\n"
        "Могу рассказать о коллекциях, ценах и помочь с заказом.\n"
        "Напишите «покажи обои» или /catalog",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — начать диалог\n"
        "/catalog — каталог обоев\n"
        "/help — эта справка\n\n"
        "Примеры фраз:\n"
        "• «Покажи обои»\n"
        "• «Обои для спальни»\n"
        "• «Сколько стоит Лесная сказка»\n"
        "• «Хочу купить»",
    )


async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(catalog_summary(), parse_mode="Markdown")


async def run_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    replica = update.message.text
    answer = bot(replica)
    try:
        await update.message.reply_text(answer, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(answer)

    logger.info("replica=%r answer=%r stats=%s", replica, answer, stats)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Укажите TELEGRAM_BOT_TOKEN в файле .env (см. .env.example)"
        )

    info = initialize()
    logger.info("Bot initialized: %s", info)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_bot))

    logger.info("Starting Telegram bot polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
