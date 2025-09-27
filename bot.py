from telethon import TelegramClient, events
import time
import asyncio

# ====== CONFIG ======
COOLDOWN_SECONDS = 3600  # 1 hour cooldown
AUTO_REPLY_TEXT = "Owner is off right now. I'll let them know you messaged."
# ====================

last_replied = {}  # user_id -> last reply timestamp
clients = {}       # store running clients if needed to stop later


async def start_auto_reply(api_id, api_hash, session_name, phone_number):
    client = TelegramClient(session_name, api_id, api_hash)

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.is_private:  # Only reply in PMs
            return

        sender = await event.get_sender()
        if sender is None:
            return

        user_id = sender.id
        me = await client.get_me()
        if user_id == me.id:
            return  # ignore self

        now = time.time()
        last = last_replied.get(user_id, 0)
        if now - last < COOLDOWN_SECONDS:
            return  # cooldown

        await event.reply(AUTO_REPLY_TEXT)
        last_replied[user_id] = now

        print(f"[{time.strftime('%H:%M:%S')}] Auto-replied to {sender.first_name} ({user_id})")

    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"\n✅ Logged in as: {me.first_name} ({me.id})")
    print("🤖 Auto-reply is running... Press Ctrl+C to stop\n")

    clients[session_name] = client
    await client.run_until_disconnected()


def main_menu():
    while True:
        print("\n=== TELEGRAM AUTO-REPLY BOT ===")
        print("1. Start Auto-reply Bot")
        print("2. Stop Auto-reply Bot")
        print("3. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            api_id = int(input("Enter API ID: ").strip())
            api_hash = input("Enter API HASH: ").strip()
            session_name = input("Enter session name: ").strip()
            phone_number = input("Enter your phone number (with country code): ").strip()
            print("\nStarting bot...\n")

            asyncio.run(start_auto_reply(api_id, api_hash, session_name, phone_number))
            print("\nReturning to main menu...\n")

        elif choice == "2":
            if not clients:
                print("No running bot found.")
            else:
                for name, client in clients.items():
                    asyncio.run(client.disconnect())
                    print(f"Bot '{name}' stopped.")
                clients.clear()

        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
