import os
import asyncio
import random
import nest_asyncio
import threading
from datetime import datetime, time

from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

# Импорт обработчиков
from handlers import start, handle_sentmsg, handle_sentmsg_ai
from db import init_db

# --- 1️⃣ Подгружаем .env ---
load_dotenv()
nest_asyncio.apply()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")


# --- 2️⃣ Фейковый HTTP-сервер для Render ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running on Render!")


def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))  # Render задаёт PORT автоматически
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Dummy HTTP server running on port {port}")
    server.serve_forever()


# --- 3️⃣ Функция планирования сообщений ---
def schedule_random_ai_messages(scheduler, app):
    """
    Планирует 4 случайных запуска handle_sentmsg_ai между 10:00 и 21:00.
    """
    now = datetime.now()
    today = now.date()
    times = []

    for _ in range(4):
        hour = random.randint(10, 20)
        minute = random.randint(0, 59)
        t = datetime.combine(today, time(hour, minute))
        if t > now:
            times.append(t)

    times.sort()
    for t in times:
        print(f"Scheduled AI message at {t.strftime('%H:%M')}")
        scheduler.add_job(
            handle_sentmsg_ai,
            trigger=DateTrigger(run_date=t),
            args=(app.bot, None),
        )


# --- 4️⃣ Основная логика бота ---
async def main():
    # Инициализация БД
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    await app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("sentmsg", "Send text to all subscribers (admin only)"),
        BotCommand("sentmsg_ai", "Send AI-generated message to all (admin only)")
    ])

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()

    scheduler.add_job(
        schedule_random_ai_messages,
        trigger="cron",
        hour=0,
        minute=5,
        args=[scheduler, app],
    )

    schedule_random_ai_messages(scheduler, app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sentmsg", handle_sentmsg))
    app.add_handler(CommandHandler("sentmsg_ai", handle_sentmsg_ai))

    print("Telegram bot started.")
    await app.run_polling()


# --- 5️⃣ Запуск ---
if __name__ == "__main__":
    # Запускаем HTTP-сервер в фоне, чтобы Render не ругался
    threading.Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
