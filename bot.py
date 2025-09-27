from telethon import TelegramClient, events
import time
import asyncio

# ===== CONFIG =====
AUTO_REPLY_TEXT = "Owner is off right now. I'll let them know you messaged."
COOLDOWN_SECONDS = 1  # 1 hour cooldown per user
# ==================

running_clients = {}  # session_name -> client
last_replied_dict = {}  # session_name -> {user_id -> timestamp}


async def auto_reply_bot(api_id, api_hash, session_name, phone_number):
    client = TelegramClient(session_name, api_id, api_hash)
    last_replied = {}
    last_replied_dict[session_name] = last_replied

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
        print(f"[{time.strftime('%H:%M:%S')}] [{session_name}] Auto-replied to {sender.first_name} ({user_id})")

    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"✅ [{session_name}] Logged in as: {me.first_name} ({me.id})")
    print(f"🤖 [{session_name}] Auto-reply is running...")

    running_clients[session_name] = client
    try:
        await client.run_until_disconnected()
    finally:
        running_clients.pop(session_name, None)
        last_replied_dict.pop(session_name, None)


def main_menu():
    print("\n=== TELEGRAM AUTO-REPLY BOT MENU ===")
    print("1. Run a new Auto-Reply Bot")
    print("2. Show Running Sessions")
    print("3. Stop a Session")
    print("4. Exit")
    choice = input("Choose an option: ").strip()
    return choice


async def run():
    while True:
        choice = main_menu()

        if choice == "1":
            # Input details for a new session
            api_id = int(input("Enter API ID: ").strip())
            api_hash = input("Enter API Hash: ").strip()
            session_name = input("Enter Session Name (file will be created): ").strip()
            phone_number = input("Enter your Phone Number (with country code): ").strip()

            # Start bot in background
            asyncio.create_task(auto_reply_bot(api_id, api_hash, session_name, phone_number))
            print(f"✅ [{session_name}] Bot is starting in background...\n")

        elif choice == "2":
            # Show running sessions
            if running_clients:
                print("🔹 Running Sessions:")
                for s in running_clients:
                    print(f" - {s}")
            else:
                print("No sessions running currently.")

        elif choice == "3":
            # Stop a specific session
            if running_clients:
                print("Select a session to stop:")
                for idx, s in enumerate(running_clients, start=1):
                    print(f"{idx}. {s}")
                sel = input("Enter number: ").strip()
                try:
                    sel_idx = int(sel) - 1
                    session_to_stop = list(running_clients.keys())[sel_idx]
                    client_to_stop = running_clients[session_to_stop]
                    await client_to_stop.disconnect()
                    print(f"✅ Session '{session_to_stop}' stopped.")
                except (ValueError, IndexError):
                    print("Invalid selection!")
            else:
                print("No sessions running to stop.")

        elif choice == "4":
            # Exit all sessions
            print("Stopping all sessions and exiting...")
            for client in list(running_clients.values()):
                await client.disconnect()
            break

        else:
            print("Invalid option! Try again.")


if __name__ == "__main__":
    asyncio.run(run())
