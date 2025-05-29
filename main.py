import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from dotenv import load_dotenv
import openai
import uvicorn

# Load environment variables
load_dotenv()

# Get tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")

# OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Храни API ключ в Render как OPENAI_API_KEY
    base_url="https://api.intelligence.io.solutions/api/v1/",
)

# FastAPI app
app = FastAPI()

# Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# === AI логика ===
async def ask_ai(question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            stream=False,
            max_completion_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me any question, and I will try to answer using AI 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await ask_ai(user_text)
    await update.message.reply_text(reply)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Run on startup
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()

@app.on_event("shutdown")
async def shutdown():
    await application.stop()
    await application.shutdown()

# Webhook
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# Health
@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
