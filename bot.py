from telethon import TelegramClient, events
import time
import asyncio
import json
import os

# ====== CONFIG ======
COOLDOWN_SECONDS = 1  # 1 hour cooldown
AUTO_REPLY_TEXT = "𝘾𝙐𝙍𝙍𝙀𝙉𝙏𝙇𝙔 𝙊𝙁𝙁𝙇𝙄𝙉𝙀!🔕  𝙋𝙇𝙀𝘼𝙎𝙀 𝘿𝙍𝙊𝙋 𝙔𝙊𝙐𝙍 𝙈𝙀𝙎𝙎𝘼𝙂𝙀, 𝙒𝙄𝙇𝙇 𝙍𝙀𝙎𝙋𝙊𝙉𝘿 𝙏𝙊 𝙔𝙊𝙐 𝙇𝘼𝙏𝙀𝙍!"
CONFIG_FILE = "config.json"
# ====================

last_replied = {}  # user_id -> last reply timestamp
clients = {}       # session_name -> client object
API_ID = None
API_HASH = None


def load_config():
    """Load API credentials from config.json if exists"""
    global API_ID, API_HASH
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            API_ID = data.get("api_id")
            API_HASH = data.get("api_hash")


def save_config(api_id, api_hash):
    """Save API credentials into config.json"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_id": api_id, "api_hash": api_hash}, f, indent=4)


async def start_auto_reply(session_name, phone_number):
    client = TelegramClient(session_name, API_ID, API_HASH)

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.is_private:
            return

        sender = await event.get_sender()
        if sender is None:
            return

        user_id = sender.id
        me = await client.get_me()
        if user_id == me.id:
            return

        now = time.time()
        last = last_replied.get(user_id, 0)
        if now - last < COOLDOWN_SECONDS:
            return

        await event.reply(AUTO_REPLY_TEXT)
        last_replied[user_id] = now
        print(f"[{time.strftime('%H:%M:%S')}] Auto-replied to {sender.first_name} ({user_id})")

    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"\n✅ Logged in as: {me.first_name} ({me.id}) [Session: {session_name}]")
    print("🤖 Auto-reply is running... (Press Ctrl+C to return to main menu)\n")

    clients[session_name] = (client, me.first_name, me.id)

    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print(f"\n⏹️ Bot stopped for session: {session_name}\n")


def main_menu():
    global API_ID, API_HASH

    # Load config if available
    load_config()

    # If no API ID/HASH saved, ask once
    if API_ID is None or API_HASH is None:
        print("=== TELEGRAM AUTO-REPLY BOT SETUP ===")
        API_ID = int(input("Enter API ID: ").strip())
        API_HASH = input("Enter API HASH: ").strip()
        save_config(API_ID, API_HASH)
        print("✅ Saved API credentials in config.json\n")

    # Main loop
    while True:
        print("\n=== TELEGRAM AUTO-REPLY BOT ===")
        print("1. Start Auto-reply Bot")
        print("2. Stop All Bots")
        print("3. Show Running Sessions")
        print("4. Stop Specific Session")
        print("5. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            session_name = input("Enter session name: ").strip()
            phone_number = input("Enter your phone number (with country code): ").strip()
            print("\nStarting bot...\n")
            try:
                asyncio.run(start_auto_reply(session_name, phone_number))
            except Exception as e:
                print(f"❌ Error: {e}")
            print("\nReturning to main menu...\n")

        elif choice == "2":
            if not clients:
                print("⚠️ No running bots found.")
            else:
                for name, (client, _, _) in list(clients.items()):
                    asyncio.run(client.disconnect())
                    print(f"⏹️ Bot '{name}' stopped.")
                clients.clear()

        elif choice == "3":
            if not clients:
                print("⚠️ No running sessions.")
            else:
                print("\n=== Running Sessions ===")
                for name, (_, user, uid) in clients.items():
                    print(f"• {name} → {user} ({uid})")

        elif choice == "4":
            if not clients:
                print("⚠️ No running sessions to stop.")
            else:
                print("\nSelect session to stop:")
                sessions = list(clients.keys())
                for i, name in enumerate(sessions, 1):
                    print(f"{i}. {name}")
                try:
                    idx = int(input("Enter choice: ").strip()) - 1
                    if 0 <= idx < len(sessions):
                        name = sessions[idx]
                        client, _, _ = clients[name]
                        asyncio.run(client.disconnect())
                        print(f"⏹️ Bot '{name}' stopped.")
                        del clients[name]
                    else:
                        print("⚠️ Invalid choice.")
                except ValueError:
                    print("⚠️ Invalid input.")

        elif choice == "5":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
