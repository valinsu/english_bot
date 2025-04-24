from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

from handlers import start_command, word_command

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()

app.bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("word", "Get a random word")
])

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("word", word_command))

app.run_polling()

print("Bot is running...")
