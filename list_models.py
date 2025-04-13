import google.generativeai as genai
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("API ключ не найден. Проверь .env файл.")

# Настраиваем genai с API ключом
genai.configure(api_key=api_key)

# Выводим список моделей
models = genai.list_models()
for model in models:
    print(model.name)

# Пробуем вызвать одну модель
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Hello, Gemini!")
    print("\nОтвет от модели:")
    print(response.text)
except Exception as e:
    print("❌ Ошибка при генерации контента:", e)
