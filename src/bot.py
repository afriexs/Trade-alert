from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import main_menu, asset_menu, upgrade_menu, settings_menu, interval_menu
from appwrite_client import db
from rate_history import get_top_movers
import config, time, traceback, sys, os, json

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

    print("BUTTON CLICKED:", query.data, flush=True)

    # -------- GET USER DATA --------
    user = db.get_document(
        database_id=config.APPWRITE_DB,
        collection_id=config.APPWRITE_COLLECTION,
        document_id=chat_id
    )

    assets = json.loads(user.get("assets", "[]"))

    # -------- SELECT ASSETS MENU --------
    if query.data == "select_assets":
        query.message.edit_text(
            "Choose asset type:",
            reply_markup=asset_menu()
        )

    # -------- SELECT CRYPTO --------
    elif query.data in ["asset_crypto", "asset_forex"]:
        chat_id = str(query.message.chat_id)

        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        )

        assets = user.assets if user.assets else []

        selected = "crypto" if query.data == "asset_crypto" else "forex"

        if selected not in assets:
            assets.append(selected)

        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"assets": assets}
        )

        query.answer(f"{selected.capitalize()} added ✅")


    # -------- TOGGLE ASSET --------
    elif query.data.startswith("toggle_"):
        asset = query.data.replace("toggle_", "")

        if asset in assets:
            assets.remove(asset)
        else:
            assets.append(asset)

        # SAVE BACK
        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={
                "assets": json.dumps(assets)
            }
        )

        # REFRESH MENU
        mode = context.user_data.get("mode")

        if mode == "crypto":
            query.message.edit_text(
                "Select Crypto:",
                reply_markup=crypto_list_menu(assets)
            )
        else:
            query.message.edit_text(
                "Select Forex:",
                reply_markup=forex_list_menu(assets)
            )

    # -------- DONE --------
    elif query.data == "done_assets":
        query.message.edit_text(
            f"✅ Assets saved:\n{', '.join(assets) if assets else 'None'}",
            reply_markup=main_menu()
    )

# ---------------- HANDLERS ----------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

# ---------------- START ----------------
updater.start_polling(
    drop_pending_updates=True,
    allowed_updates=["message", "callback_query"]
)
updater.idle()
