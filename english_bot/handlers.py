from telegram import Update
from telegram.ext import ContextTypes
import json
import random
import os

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi bro, let's learn some English words together!")
    await update.message.reply_text("Use /word to get a random word")

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_dir = os.path.dirname(__file__)
        path_to_json = os.path.join(current_dir, "lessons", "words.json")
        
        with open(path_to_json, "r", encoding="utf-8") as f:
            words = json.load(f)
    
        word_data = random.choice(words)
        response = f"Word: *{word_data['word']}*\nRU Translation: {word_data['translation']}\nExample: _{word_data['example']}_"
        await update.message.reply_markdown_v2(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
