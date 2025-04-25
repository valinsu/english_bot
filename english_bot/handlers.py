from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_dir = os.path.dirname(__file__)
        path_to_json = os.path.join(current_dir, "lessons", "words.json")
        
        with open(path_to_json, "r", encoding="utf-8") as f:
            words = json.load(f)
    
        word_data = random.choice(words)
        word = word_data['word']    
        correct = word_data['translation']
        wrong_answers = word_data["wrong_answers"] if "wrong_answers" in word_data else []

        options = [correct] + wrong_answers
        random.shuffle(options)

        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"{word}|{opt}")] for opt in options
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Choose the correct translation of *{word}*:", parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    word, chosen = query.data.split("|")

    current_dir = os.path.dirname(__file__)
    path_to_json = os.path.join(current_dir, "lessons", "words.json")
    
    with open(path_to_json, "r", encoding="utf-8") as f:
        words = json.load(f)
    
    word_data = next((w for w in words if w['word'] == word), None)

    if word_data:
        correct = word_data['translation']
        if chosen == correct:
            await query.edit_message_text(f"Correct! *{word}* means _{correct}_", parse_mode="Markdown")
        else:
            await query.edit_message_text(f"Wrong! *{word}* means _{correct}_, not _{chosen}_", parse_mode="Markdown")
    else:
        await query.edit_message_text("Somerhing went wrong")