from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
import random
import os

from storage import update_user_data

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
       
        user = update.effective_user
        update_user_data(user.id, user.username, seen_word=word_data['word'])
        await update.message.reply_markdown_v2(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)

        current_dir = os.path.dirname(__file__)
        path_to_user_data = os.path.join(current_dir, "data", "users.json")
        path_to_words = os.path.join(current_dir, "lessons", "words.json")      

        if not os.path.exists(path_to_user_data):
            await update.message.reply_text("You haven't seen any words yet! Use /word first.")
            return
        
        with open(path_to_user_data, "r", encoding="utf-8") as f:
            data = json.load(f)

        user_data = data.get(user_id)
        if not user_data:
            await update.message.reply_text("You haven't seen any words yet! Use /word first.")
            return

        user_words = user_data.get("words_seen", [])
        if not user_words:
            await update.message.reply_text("You haven't seen any words yet! Use /word first.")
            return

        with open(path_to_words, "r", encoding="utf-8") as f:
            words = json.load(f)

        seen_words = [word for word in words if word['word'] in user_words]

        if not seen_words:
            await update.message.reply_text("Couldn't find matching words in the dataset.")
            return

        word_data = random.choice(seen_words)
        word = word_data['word']    
        correct = word_data['translation']
        wrong_answers = word_data.get("wrong_answers", [])

        options = [correct] + wrong_answers
        random.shuffle(options)

        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"{word}|{opt}")] for opt in options
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Choose the correct translation of *{word}*:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user

    word, chosen = query.data.split("|")

    current_dir = os.path.dirname(__file__)
    path_to_json = os.path.join(current_dir, "lessons", "words.json")
    
    with open(path_to_json, "r", encoding="utf-8") as f:
        words = json.load(f)
    
    word_data = next((w for w in words if w['word'] == word), None)

    if word_data:
        correct = word_data['translation']
        if chosen == correct:
            update_user_data(user.id, user.username, correct_word=word)
            await query.edit_message_text(f"Correct! *{word}* means _{correct}_", parse_mode="Markdown")
        else:
            update_user_data(user.id, user.username, wrong_word=word)
            await query.edit_message_text(f"Wrong! *{word}* means _{correct}_, not _{chosen}_", parse_mode="Markdown")
    else:
        await query.edit_message_text("Somerhing went wrong")


async def my_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    current_dir = os.path.dirname(__file__)
    path_to_user_data = os.path.join(current_dir, "data", "users.json")

    if not os.path.exists(path_to_user_data):
        await update.message.reply_text("You haven't seen any words yet! Use /word first.")
        return

    with open(path_to_user_data, "r", encoding="utf-8") as f:
        data = json.load(f)

    if user_id not in data:
        await update.message.reply_text("You haven't seen any words yet! Use /word first.")
        return

    user_data = data[user_id]
    seen_words = user_data.get("words_seen", [])
    correct_answers = user_data.get("correct_answers", [])
    wrong_words = user_data.get("wrong_words", [])

    if not seen_words:
        await update.message.reply_text("You haven't seen any words yet! Use /word first.")
        return

    response = (
        f"Seen words: {len(seen_words)}\n"
        f"Correct answers: {len(correct_answers)}\n"
        f"Wrong answers: {len(wrong_words)}"
    )

    await update.message.reply_text(response)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    current_dir = os.path.dirname(__file__)
    path__to_user_data = os.path.join(current_dir, "data", "users.json")

    if not os.path.exists(path__to_user_data):
        await update.message.reply_text("No data to reset")
        return
    
    with open(path__to_user_data, "r", encoding="utf-8") as f:
        data = json.load(f)

    if user_id in data:
        del data[user_id]

        with open(path__to_user_data, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)    
        
        await update.message.reply_text("Your data has been reset")
    else:
        await update.message.reply_text("No data found for you")