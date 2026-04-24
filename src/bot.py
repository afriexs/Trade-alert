from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import main_menu, asset_menu, upgrade_menu, settings_menu, interval_menu
from appwrite_client import db
from rate_history import get_top_movers
import config, time, traceback, os, json

time.sleep(5)

LOCK_FILE = "/tmp/bot.lock"

if os.path.exists(LOCK_FILE):
    print("Bot already running, exiting...")
    exit()

open(LOCK_FILE, "w").close()

print("BOT STARTING...", flush=True)

# ---------------- SERVER ----------------
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

# ---------------- INIT ----------------
updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

# ---------------- START ----------------
def start(update, context):
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
                "assets": [],
                "interval": 60
            }
        )

    update.message.reply_text(
        "Welcome 👋",
        reply_markup=main_menu()
    )

# ---------------- BUTTON ----------------
def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat_id)

    if query.data == "select_assets":
        context.user_data["temp_assets"] = []
        query.edit_message_text("Select assets:", reply_markup=asset_menu())

    elif query.data.startswith("asset_"):
        asset_type = query.data.split("_")[1]

        if asset_type == "both":
            context.user_data["temp_assets"] = ["crypto", "forex"]
        else:
            if "temp_assets" not in context.user_data:
                context.user_data["temp_assets"] = []
            context.user_data["temp_assets"].append(asset_type)

        query.answer(f"{asset_type} selected")

    elif query.data == "done_assets":
        selected = context.user_data.get("temp_assets", [])

        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"assets": selected}
        )

        query.edit_message_text("✅ Assets saved", reply_markup=main_menu())

    elif query.data == "settings":
        query.edit_message_text("Settings:", reply_markup=settings_menu())

    elif query.data == "interval_settings":
        query.edit_message_text("Choose interval:", reply_markup=interval_menu())

    elif query.data.startswith("interval_"):
        minutes = int(query.data.split("_")[1])

        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"interval": minutes}
        )

        query.edit_message_text(f"✅ Interval set to {minutes} mins", reply_markup=main_menu())

    elif query.data == "condition_settings":
        query.edit_message_text("Send conditions like:\nBTC > 2%\nETH < -1%")

    elif query.data == "check_top":
        crypto = get_top_movers("crypto")
        forex = get_top_movers("forex")

        text = "📈 Top Crypto (trend)\n\n"
        for c, val in crypto:
            text += f"{c} ↑ +{val}%\n"

        text += "\n💱 Top Forex (trend)\n\n"
        for f, val in forex:
            text += f"{f} ↑ +{val}%\n"

        query.edit_message_text(text)

    elif query.data == "upgrade":
        query.edit_message_text("Upgrade:", reply_markup=upgrade_menu())

# ---------------- HANDLERS ----------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

# ---------------- START ----------------
updater.start_polling(
    drop_pending_updates=True,
    allowed_updates=["message", "callback_query"]
)
updater.idle()
