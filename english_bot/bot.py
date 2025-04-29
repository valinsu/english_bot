import os
import asyncio
import nest_asyncio
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, Application
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import start_command, word_command, quiz_command, handle_answer, my_word_command, reset_command
from scheduler import send_daily_word

nest_asyncio.apply()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.bot.set_my_commands([
        BotCommand("word", "Get a random word"),
        BotCommand("quiz", "Get a quiz"),
        BotCommand("my_words", "See your words"),
        BotCommand("reset", "Reset your progress")
        ])

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_word, 'cron', hour=21, minute = 6, args=[app.bot])
    scheduler.start()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.add_handler(CommandHandler("my_words", my_word_command))
    app.add_handler(CommandHandler("reset", reset_command))

    print("Bot is running...")
    await app.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
