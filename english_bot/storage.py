import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "users.json")    

def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def update_user_data(user_id, username=None, seen_word=None, correct_word=None, wrong_word=None):
    data = load_data()
    user_id = str(user_id) 

    if user_id not in data:
        data[user_id] = {
            "username": username,
            "words_seen": [],
            "correct_answers": [],
            "wrong_word": []
        }
    if seen_word and seen_word not in data[user_id]["words_seen"]:
        data[user_id]["words_seen"].append(seen_word)

    if correct_word and correct_word not in data[user_id]["correct_answers"]:
        data[user_id]["correct_answers"].append(correct_word)
    
    if wrong_word and wrong_word not in data[user_id]["wrong_words"]:
        data[user_id]["wrong_words"].append(wrong_word)

    save_data(data)