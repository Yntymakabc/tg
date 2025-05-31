import os
import json
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time

# Загрузка переменных окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к изображению
IMAGE_PATH = "zamzam.png"

# Путь к файлу с пользователями
USERS_FILE = "users.json"

# Сообщение, которое отправляется с фото
MESSAGE_TEXT = """🌈 Свобода быть собой.
В мире, где каждый достоин принятия и любви, самовыражение — это сила. Яркие цвета, открытое сердце и смелость быть настоящим — всё это о нём. Он не боится выделаться, не скрывает свою индивидуальность и гордится тем, кто он есть.
#Pride #LoveIsLove #LGBTQ #БудьСобой

Контакты:
+996(557) 35-88-75
@samat"""

# FastAPI приложение
app = FastAPI()

# Создаем планировщик
scheduler = AsyncIOScheduler()

# Функция для загрузки пользователей
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Функция для сохранения пользователей
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохраняем ID пользователя
    user_id = update.effective_user.id
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
    
    # Отправляем приветственное сообщение с фото
    await handle_hello(update, context)

async def handle_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(IMAGE_PATH, 'rb') as photo_file:
            await update.message.reply_photo(photo=photo_file, caption=MESSAGE_TEXT)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохраняем ID пользователя
    user_id = update.effective_user.id
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        
    # Отвечаем на сообщение, если это "привет"
    text = update.message.text.lower()
    if text == "привет":
        await handle_hello(update, context)

# Функция для рассылки сообщений всем пользователям
async def broadcast_message():
    users = load_users()
    for user_id in users:
        try:
            # Отправляем фото и сообщение каждому пользователю
            with open(IMAGE_PATH, 'rb') as photo_file:
                await application.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_file,
                    caption=MESSAGE_TEXT
                )
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск и остановка бота
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    
    # Настраиваем ежедневную отправку сообщений в 22:30
    scheduler.add_job(broadcast_message, "cron", hour=22, minute=30)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
    await application.stop()
    await application.shutdown()

# Webhook для Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# Проверка статуса
@app.get("/")
def root():
    return {"status": "ok"}

# Запуск локально
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
