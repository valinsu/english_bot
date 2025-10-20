import os
import asyncio
import random
import nest_asyncio
from datetime import datetime, time, timedelta

from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

# Импорт обработчиков
from handlers import start, handle_sentmsg, handle_sentmsg_ai
from db import init_db

# Подгружаем .env
load_dotenv()

nest_asyncio.apply()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in .env")


def schedule_random_ai_messages(scheduler, app):
    """
    Планирует 4 случайных запуска handle_sentmsg_ai между 10:00 и 21:00.
    """
    now = datetime.now()
    today = now.date()
    times = []

    # Генерируем 4 случайных времени между 10:00 и 21:00
    for _ in range(4):
        hour = random.randint(10, 20)  # до 20 включительно, т.к. 21:00 — верхняя граница
        minute = random.randint(0, 59)
        t = datetime.combine(today, time(hour, minute))
        if t > now:
            times.append(t)

    # Сортируем для аккуратности
    times.sort()

    for t in times:
        print(f"🕒 Scheduled AI message at {t.strftime('%H:%M')}")
        scheduler.add_job(
            handle_sentmsg_ai,
            trigger=DateTrigger(run_date=t),
            args=(app.bot, None),  # передаём bot; update=None, если не вызывается вручную
        )


async def main():
    # Инициализация базы данных
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команды
    await app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("sentmsg", "Send text to all subscribers (admin only)"),
        BotCommand("sentmsg_ai", "Send AI-generated message to all (admin only)")
    ])

    # Планировщик
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()

    # Ежедневное переназначение случайных запусков
    scheduler.add_job(
        schedule_random_ai_messages,
        trigger="cron",
        hour=0,
        minute=5,
        args=[scheduler, app],
    )

    # Первый запуск планирования
    schedule_random_ai_messages(scheduler, app)

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sentmsg", handle_sentmsg))
    app.add_handler(CommandHandler("sentmsg_ai", handle_sentmsg_ai))

    print("Bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
