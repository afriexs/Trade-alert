from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import main_menu, asset_menu, upgrade_menu, settings_menu, interval_menu, crypto_list_menu, forex_list_menu, condition_asset_menu, condition_list_menu, remove_condition_menu, add_condition_type_menu
from appwrite_client import db
from rate_history import get_top_movers
import config, time, traceback, sys, os, json
import uuid


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
user_selection = {}

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
                "interval": 60,
                "conditions": {}
            }
        )

    update.message.reply_text(
        "Welcome 👋",
        reply_markup=main_menu()
    )

# ---------------- Menu ----------------
def menu(update, context):
    update.message.reply_text(
        "Main Menu",
        reply_markup=main_menu()
    )

# ---------------- BUTTON ----------------
def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat_id)

    # init user selection if not exists
    if chat_id not in user_selection:
        user_selection[chat_id] = {
            "assets": []
        }

    data = query.data
    print("BUTTON CLICKED:", data, flush=True)

    # ---------------- MAIN MENU ----------------
    if data == "select_assets":
        query.message.edit_text(
            "Choose asset type:",
            reply_markup=asset_menu()
        )

    elif data == "asset_crypto":
        selected = user_selection[chat_id]["assets"]
        query.message.edit_text(
            "Select Crypto:",
            reply_markup=crypto_list_menu(selected)
        )

    elif data == "asset_forex":
        selected = user_selection[chat_id]["assets"]
        query.message.edit_text(
            "Select Forex:",
            reply_markup=forex_list_menu(selected)
        )

    # ---------------- TOGGLE ASSETS ----------------
    elif data.startswith("toggle_"):
        asset = data.split("_")[1]

        if asset in user_selection[chat_id]["assets"]:
            user_selection[chat_id]["assets"].remove(asset)
        else:
            user_selection[chat_id]["assets"].append(asset)

        selected = user_selection[chat_id]["assets"]

        # Detect which menu to show again
        if asset in ["BTC", "ETH", "DOGE", "SOL", "BNB"]:
            query.message.edit_text(
                "Select Crypto:",
                reply_markup=crypto_list_menu(selected)
            )
        else:
            query.message.edit_text(
                "Select Forex:",
                reply_markup=forex_list_menu(selected)
            )

    # ---------------- SAVE ----------------
    elif data == "done_assets":
        selected = user_selection[chat_id]["assets"]

        # save to Appwrite
        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"assets": selected}
        )

        query.message.edit_text(
            f"✅ Saved Assets:\n\n{', '.join(selected) if selected else 'None'}",
            reply_markup=main_menu()
        )

    # ---------------- OTHER BUTTONS ----------------
    elif data == "upgrade":
        query.message.edit_text("Upgrade your plan:", reply_markup=upgrade_menu())

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

    elif data.startswith("cond_asset_"):
        asset = data.split("_")[2]

        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        ).dict()

        conditions = user.data.get("conditions", {}).data.get(asset, [])

        query.edit_message_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, conditions)
        )

    elif data.startswith("addcond_"):
        asset = data.split("_")[1]

        query.edit_message_text(
            f"{asset} - Choose type:",
            reply_markup=add_condition_type_menu(asset)
        )

    elif data.startswith("addtype_"):
        _, asset, ctype = data.split("_")

        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        ).dict()

        conditions = user.get("conditions", {})

        new_cond = {
            "id": str(uuid.uuid4())[:6],
            "type": ctype,
            "value": 2
        }

        conditions.setdefault(asset, []).append(new_cond)

        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"conditions": conditions}
        )

        # 🔥 IMPORTANT: reload updated list
        updated_conditions = conditions.get(asset, [])

        query.edit_message_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, updated_conditions)
        )

    elif data.startswith("removecond_"):
        asset = data.split("_")[1]

        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        )

        conditions = user.get("conditions", {}).get(asset, [])

        query.edit_message_text(
            f"Remove condition for {asset}:",
            reply_markup=remove_condition_menu(asset, conditions)
        )

    elif data.startswith("delcond_"):
        _, asset, cid = data.split("_")

        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        )

        conditions = user.get("conditions", {})

        if asset in conditions:
            conditions[asset] = [c for c in conditions[asset] if c["id"] != cid]

        db.update_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id,
            data={"conditions": conditions}
        )

        # 🔥 IMPORTANT: reload updated list
        updated_conditions = conditions.data.get(asset, [])

        query.edit_message_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, updated_conditions)
        )

    elif data == "condition_settings":
        user = db.get_document(
            database_id=config.APPWRITE_DB,
            collection_id=config.APPWRITE_COLLECTION,
            document_id=chat_id
        ).dict()

        assets = user.get("assets", [])
        print("passed assets:", assets)

        if not assets:
            query.edit_message_text(
                "⚠ You haven't selected any assets yet.\n\nPlease select assets first.",
                reply_markup=asset_menu()
            )
            return

        query.edit_message_text(
            "Select asset:",
            reply_markup=condition_asset_menu(assets)
        )

    elif query.data == "back_main":
        query.edit_message_text("Main Menu:", reply_markup=main_menu())

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


# ---------------- HANDLERS ----------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

# ---------------- START ----------------
updater.start_polling(
    drop_pending_updates=True,
    allowed_updates=["message", "callback_query"]
)
updater.idle()
