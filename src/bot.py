from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import main_menu, asset_menu, upgrade_menu
from appwrite_client import db
import config, time
import traceback
import sys
import os
import time
time.sleep(5)

LOCK_FILE = "/tmp/bot.lock"

if os.path.exists(LOCK_FILE):
    print("Bot already running, exiting...")
    exit()

open(LOCK_FILE, "w").close()

print("BOT STARTING...", flush=True)

# ---------------- OPTIONAL PORT SERVER (KEEP FOR RENDER) ----------------
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()


# ---------------- INIT BOT ----------------
updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher
print("BOT USER:", updater.bot.get_me(), flush=True)
    
# ---------------- START COMMAND ----------------
def start(update, context):
    print("START COMMAND RECEIVED", flush=True)
    chat_id = str(update.message.chat_id)

    try:
        db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        )
    except:
        db.create_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={
                "chat_id": chat_id,
                "plan": "free",
                "expires_at": 0,
                "amount": 10000,
                "assets": [],
                "reference_prices": {},
                "threshold": 0.01,
                "interval": 60
            }
        )

    args = context.args

    if args and args[0].startswith("paid_"):
        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={
                "plan": "standard",
                "expires_at": int(time.time()) + (30 * 86400)
            }
        )
        update.message.reply_text("✅ Subscription activated!")

    update.message.reply_text(
        "Welcome 👋\n\nTrack market moves easily.",
        reply_markup=main_menu()
    )


# ---------------- BUTTON HANDLER ----------------
def button(update, context):
    print("BUTTON CLICKED:", update.callback_query.data, flush=True)

    query = update.callback_query
    query.answer()

    if query.data == "select_assets":
        query.edit_message_text("Select assets:", reply_markup=asset_menu())

    elif query.data == "upgrade":
        query.edit_message_text("Upgrade your plan:", reply_markup=upgrade_menu())

    elif query.data == "settings":
        query.edit_message_text("⚙ Settings coming soon")

    elif query.data == "check_rate":
        query.edit_message_text("Enter /check BTC")


# ---------------- ERROR HANDLER ----------------
def error_handler(update, context):
    print("ERROR:", traceback.format_exc(), flush=True)


# ---------------- REGISTER HANDLERS ----------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

dp.add_error_handler(error_handler)


# ---------------- START BOT SAFELY ----------------
try:
    updater.start_polling(
    drop_pending_updates=True,
    timeout=30,
    read_latency=2
    )
    updater.idle()

except Exception:
    print("CRASH ERROR:")
    print(traceback.format_exc(), flush=True)
