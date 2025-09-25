from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# -------------------------------
# CONFIGURATION
# -------------------------------

# Apna bot token yaha daalein
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Agar True set karenge, bot automatic "offline" reply dega
OFFLINE_MODE = False
OFFLINE_MESSAGE = "Sorry, I am currently offline. I will reply later."

# -------------------------------
# LOGGING
# -------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------------------
# HANDLERS
# -------------------------------

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm your console bot.")
    print(f"[START] {update.message.from_user.username} started the bot.")

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user.username or update.message.from_user.first_name
    print(f"[MESSAGE] From {user}: {text}")

    # Auto-reply logic
    if OFFLINE_MODE:
        update.message.reply_text(OFFLINE_MESSAGE)
    else:
        update.message.reply_text(f"You said: {text}")

# -------------------------------
# MAIN
# -------------------------------

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command /start
    dp.add_handler(CommandHandler("start", start))
    # Text messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot started. Waiting for messages...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
