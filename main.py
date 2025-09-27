from telethon import TelegramClient, events
import time

# ====== CONFIG ======
API_ID = 22084373
API_HASH = "10d07f2b0a375075edef29f0a700a538"
SESSION_NAME = "owner_auto_reply"  # session file name (banega same folder me)
AUTO_REPLY_TEXT = "Owner is off right now. I'll let them know you messaged."
COOLDOWN_SECONDS = 3600  # 1 ghante me ek hi reply per user
# ====================

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
last_replied = {}  # user_id -> last reply timestamp

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:  # sirf PM reply kare
        return

    sender = await event.get_sender()
    if sender is None:
        return

    user_id = sender.id
    me = await client.get_me()
    if user_id == me.id:  # apne aap ko ignore karo
        return

    now = time.time()
    last = last_replied.get(user_id, 0)

    if now - last < COOLDOWN_SECONDS:
        return  # same user ko baar baar reply na kare

    await event.reply(AUTO_REPLY_TEXT)
    last_replied[user_id] = now

    print(f"[{time.strftime('%H:%M:%S')}] Auto-replied to {sender.first_name} ({user_id})")

async def main():
    await client.start()  # pehli baar chalega to number+OTP maangega
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} ({me.id})")
    print("🤖 Auto-reply is running... (Press Ctrl+C to stop)")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
