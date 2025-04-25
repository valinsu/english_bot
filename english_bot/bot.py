from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

from handlers import start_command, word_command, quiz_command, handle_answer

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # app.bot.set_my_commands([
    #     BotCommand("word", "Get a random word"),
    #     BotCommand("quiz", "Get a quiz"),
    # ])

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
