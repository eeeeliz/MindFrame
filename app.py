from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Настройка API ключа Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Инициализация модели Gemini
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# Укороченный системный промпт
system_prompt = """
You are a friendly and intelligent virtual assistant, designed to help people with their questions and tasks. You aim to be polite, clear, and helpful. Always respond in the same language in which the question was asked (if possible).

Your goal is to provide accurate and concise answers, explaining complex things in simple terms. If you're asked to create a table or a chart — do it. Pay close attention to details and try to understand the essence of the request before replying.

You are capable of processing data, assisting with studies, projects, research, and even just having a casual conversation. Keep the conversation interesting and adapt your communication style to the user: be informal if the person speaks casually, or formal if the user communicates officially.

Your main task is to be a useful, clear, and pleasant conversational partner.
"""
chat = model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])

# Пример данных чатов (можно заменить на работу с JSON)
chats = [
    {"title": "Чат сегодня", "date": datetime.now().isoformat()},
    {"title": "Чат вчера", "date": (datetime.now() - timedelta(days=1)).isoformat()},
    {"title": "Чат 5 дней назад", "date": (datetime.now() - timedelta(days=5)).isoformat()},
    {"title": "Чат 20 дней назад", "date": (datetime.now() - timedelta(days=20)).isoformat()},
]

# Работа с файлами JSON
DATA_FILE = "chats.json"

def load_chats():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chats(chats):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

# Вспомогательная функция для определения группы по дате
def get_group_for_date(date):
    now = datetime.now()
    delta = now.date() - date.date()

    if delta.days == 0:
        return 'today'
    elif delta.days == 1:
        return 'yesterday'
    elif delta.days <= 7:
        return 'last-7-days'
    elif delta.days <= 30:
        return 'last-30-days'
    else:
        return 'older'

# Маршруты
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chats", methods=["GET"])
def get_chats():
    # Возвращает список чатов из JSON или примера
    return jsonify(load_chats() if os.path.exists(DATA_FILE) else chats)

@app.route("/chats", methods=["POST"])
def add_chat():
    # Добавляет новый чат в JSON или пример
    chats = load_chats() if os.path.exists(DATA_FILE) else chats
    new_chat = {
        "title": f"Чат #{len(chats)+1}",
        "date": datetime.now().isoformat()
    }
    chats.append(new_chat)
    if os.path.exists(DATA_FILE):
        save_chats(chats)
    return jsonify(new_chat), 201

@app.route("/get_chat_history", methods=["GET"])
def get_chat_history():
    # Группирует чаты по временным категориям
    chat_history = load_chats() if os.path.exists(DATA_FILE) else chats
    grouped_chats = {"today": [], "yesterday": [], "last-7-days": [], "last-30-days": [], "older": []}

    for chat in chat_history:
        chat_date = datetime.fromisoformat(chat["date"])
        group = get_group_for_date(chat_date)
        grouped_chats[group].append(chat)

    return jsonify(grouped_chats)

@app.route("/get_response", methods=["POST"])
def get_response():
    # Обрабатывает запрос пользователя через модель Gemini
    user_input = request.form.get("user_input", "")

    try:
        response = chat.send_message(user_input)
        answer = response.text.strip()
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=5001, debug=True)