import os
import sys
from telegram import Update
from telegram.ext import ContextTypes
from db import add_subscriber, get_all_subscribers, save_sent_message, is_message_sent
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Подгружаем .env
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ADMIN_ID = os.getenv("ADMIN_ID")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = int(ADMIN_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_subscriber(user.id, user.username or "unknown")
    await update.message.reply_text("💌 Ты теперь подписан на поток милостей!")


async def handle_sentmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Только админ может использовать эту команду.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Используй: /sentmsg текст_сообщения")
        return

    text_to_send = " ".join(context.args)
    subscribers = get_all_subscribers()

    sent_count = 0
    for user_id, username in subscribers:
        if not is_message_sent(user_id, text_to_send):
            try:
                await context.bot.send_message(chat_id=user_id, text=text_to_send)
                save_sent_message(user_id, text_to_send)
                sent_count += 1
            except Exception as e:
                print(f"Не удалось отправить пользователю {user_id}: {e}")

    await update.message.reply_text(f"✅ Сообщение отправлено {sent_count} пользователям.")


async def handle_sentmsg_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Только админ может использовать эту команду.")
        return

    await update.message.reply_text("💫 Генерирую комплимент...")

    try:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://t.me/carpe_diem_events_record_bot"
            }
        )        
        

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — доброжелательный бот, который придумывает тёплые и милые комплименты на русском языке."},
                {"role": "user", "content": "Сгенерируй один короткий, оригинальный и ласковый комплимент."}
            ]
        )

        compliment = response.choices[0].message.content.strip()

        subscribers = get_all_subscribers()
        sent_count = 0
        for user_id, username in subscribers:
            if not is_message_sent(user_id, compliment):
                try:
                    await context.bot.send_message(chat_id=user_id, text=compliment)
                    save_sent_message(user_id, compliment)
                    sent_count += 1
                except Exception as e:
                    print(f"Ошибка при отправке {user_id}: {e}")

        await update.message.reply_text(f"Комплимент отправлен {sent_count} пользователям:\n\n{compliment}")

    except Exception as e:
        await update.message.reply_text(f"Ошибка при генерации: {e}")
