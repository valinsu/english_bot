import os
import json
import random


current_dir = os.path.dirname(__file__)
users_path = os.path.join(current_dir, "data", "users.json")
words_path = os.path.join(current_dir, "lessons", "words.json")

async def send_daily_word(bot):
    print("Sending daily word...")
    if not os.path.exists(users_path) or not os.path.exists(words_path):
        return

    with open(users_path, "r", encoding="utf-8") as f:
        users_data = json.load(f)

    with open(words_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    for user_id, user_data in users_data.items():
        seen = user_data.get("words_seen", [])
        unseen_words = [w for w in words if w["word"] not in seen]

        if not unseen_words:
            continue

        word = random.choice(unseen_words)
        message = f"Daily Word:\n*{word['word']}* — {word['translation']}"

        try:
            await bot.send_message(chat_id=int(user_id), text=message, parse_mode="Markdown")
            seen.append(word["word"])
            user_data["words_seen"] = seen
        except Exception as e:
            print(f"Error sending to {user_id}: {e}")

    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
