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
import openai
import uvicorn

# Load environment variables
load_dotenv()

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client (DeepSeek or compatible)
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.intelligence.io.solutions/api/v1/",
)

# FastAPI app
app = FastAPI()

# Telegram bot
application = Application.builder().token(BOT_TOKEN).build()

# === AI Logic ===
async def ask_ai(question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a direct and concise assistant. "
                        "Always answer briefly and factually. "
                        "Do not explain your reasoning or thoughts. "
                        "Never say 'I think' or 'maybe'. Just answer clearly."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            stream=False,
            max_completion_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка: {str(e)}"

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Задай мне вопрос, и я постараюсь ответить кратко и чётко 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await ask_ai(user_text)
    await update.message.reply_text(reply)

# === Register Handlers ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Startup / Shutdown ===
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()

@app.on_event("shutdown")
async def shutdown():
    await application.stop()
    await application.shutdown()

# === Webhook ===
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# === Health check ===
@app.get("/")
def root():
    return {"status": "ok"}

# === Local run ===
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
