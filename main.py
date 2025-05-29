import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Get bot token
TOKEN = os.getenv("BOT_TOKEN")

# Initialize Telegram bot application
application = Application.builder().token(TOKEN).build()

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.first_name}! Welcome to the bot 🤖")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show help")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# === Critical: run Telegram bot in background ===
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()  # <== this runs the bot in background

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

# === Webhook endpoint ===
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# === Health check ===
@app.get("/")
def root():
    return {"status": "ok"}

# Local run
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
