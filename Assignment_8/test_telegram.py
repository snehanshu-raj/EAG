from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from credentials import config
import asyncio

BOT_TOKEN = config.telegram_token

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received a /start command")
    await update.message.reply_text("Hey there! 👋 I'm alive and listening!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    incoming_text = update.message.text
    print(f"Received message: {incoming_text}")

    processed_text = incoming_text.upper()
    await update.message.reply_text(f"You said: {processed_text}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
