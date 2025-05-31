import os
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

# Загрузка переменных окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к изображению
IMAGE_PATH = "zamzam.png"

# Сообщение, которое отправляется с фото
MESSAGE_TEXT = """🌈 Свобода быть собой.
В мире, где каждый достоин принятия и любви, самовыражение — это сила. Яркие цвета, открытое сердце и смелость быть настоящим — всё это о нём. Он не боится выделаться, не скрывает свою индивидуальность и гордится тем, кто он есть.
#Pride #LoveIsLove #LGBTQ #БудьСобой

Контакты:
+996(557) 35-88-75
@samat"""

# FastAPI приложение
app = FastAPI()

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Directly call handle_hello to send the photo and message
    await handle_hello(update, context)

async def handle_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(IMAGE_PATH, 'rb') as photo_file:
            await update.message.reply_photo(photo=photo_file, caption=MESSAGE_TEXT)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "привет":
        await handle_hello(update, context)

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск и остановка бота
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()

@app.on_event("shutdown")
async def shutdown():
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
