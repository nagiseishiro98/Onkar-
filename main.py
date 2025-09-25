import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Token (Render Environment → BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")

# /start command
def start(update, context):
    update.message.reply_text("👋 Hi! I’m your bot. Type /help to see what I can do.")

# /help command
def help_command(update, context):
    update.message.reply_text(
        "Here are my commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/about - About this bot\n"
    )

# /about command
def about(update, context):
    update.message.reply_text("⚡ This is a demo Telegram bot running 24/7 on Render!")

# Any text message → Echo reply
def echo(update, context):
    update.message.reply_text(f"You said: {update.message.text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about))

    # Normal text
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
