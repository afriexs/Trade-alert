from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update

from ui import (
    main_menu,
    asset_menu,
    upgrade_menu,
    settings_menu,
    interval_menu,
    crypto_list_menu,
    forex_list_menu,
    condition_asset_menu,
    condition_list_menu,
    remove_condition_menu,
    add_condition_type_menu
)

from appwrite_client import tables
from rate_history import get_top_movers

import config
import time
import traceback
import os
import uuid

# =========================================================
# STARTUP
# =========================================================

time.sleep(5)

LOCK_FILE = "/tmp/bot.lock"

if os.path.exists(LOCK_FILE):
    print("Bot already running, exiting...")
    exit()

open(LOCK_FILE, "w").close()

print("BOT STARTING...", flush=True)

# =========================================================
# OPTIONAL WEB SERVER FOR RENDER
# =========================================================

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

# =========================================================
# TELEGRAM BOT INIT
# =========================================================

updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

# =========================================================
# MEMORY
# =========================================================

user_selection = {}

CRYPTO_LIST = ["BTC", "ETH", "DOGE", "SOL", "BNB"]
FOREX_LIST = ["USD", "EUR", "GBP", "JPY", "NGN"]

# =========================================================
# APPWRITE HELPERS
# =========================================================

def get_user(chat_id):

    try:
        user = tables.get_row(
            database_id=config.APPWRITE_DB,
            table_id=config.APPWRITE_COLLECTION,
            row_id=chat_id
        )

        return user

    except Exception as e:
        print("GET USER ERROR:", e)

        return None


def create_user(chat_id):

    try:
        tables.create_row(
            database_id=config.APPWRITE_DB,
            table_id=config.APPWRITE_COLLECTION,
            row_id=chat_id,
            data={
                "chat_id": chat_id,
                "plan": "free",
                "assets": [],
                "interval": 60,
                "conditions": {}
            }
        )

        print("USER CREATED:", chat_id)

    except Exception as e:
        print("CREATE USER ERROR:", e)


def update_user(chat_id, data):

    try:
        tables.update_row(
            database_id=config.APPWRITE_DB,
            table_id=config.APPWRITE_COLLECTION,
            row_id=chat_id,
            data=data
        )

        print("USER UPDATED:", chat_id)

    except Exception as e:
        print("UPDATE USER ERROR:", e)

# =========================================================
# START COMMAND
# =========================================================

def start(update, context):

    chat_id = str(update.message.chat_id)

    user = get_user(chat_id)

    if not user:
        create_user(chat_id)

    update.message.reply_text(
        "Welcome 👋\n\nTrack market movements easily.",
        reply_markup=main_menu()
    )

# =========================================================
# MENU COMMAND
# =========================================================

def menu(update, context):

    update.message.reply_text(
        "Main Menu",
        reply_markup=main_menu()
    )

# =========================================================
# BUTTON HANDLER
# =========================================================

def button(update, context):

    query = update.callback_query
    query.answer()

    chat_id = str(query.message.chat_id)
    data = query.data

    print("BUTTON CLICKED:", data, flush=True)

    # -----------------------------------------------------
    # INIT MEMORY
    # -----------------------------------------------------

    if chat_id not in user_selection:

        user_selection[chat_id] = {
            "assets": []
        }

    # =====================================================
    # MAIN MENU
    # =====================================================

    if data == "select_assets":

        query.message.edit_text(
            "Choose asset type:",
            reply_markup=asset_menu()
        )

    # =====================================================
    # ASSET MENUS
    # =====================================================

    elif data == "asset_crypto":

        selected = user_selection[chat_id]["assets"]

        query.message.edit_text(
            "Select Crypto Assets:",
            reply_markup=crypto_list_menu(selected)
        )

    elif data == "asset_forex":

        selected = user_selection[chat_id]["assets"]

        query.message.edit_text(
            "Select Forex Assets:",
            reply_markup=forex_list_menu(selected)
        )

    elif data == "asset_both":

        selected = user_selection[chat_id]["assets"]

        query.message.edit_text(
            "Select Crypto Assets:",
            reply_markup=crypto_list_menu(selected)
        )

    # =====================================================
    # TOGGLE ASSETS
    # =====================================================

    elif data.startswith("toggle_"):

        asset = data.split("_")[1]

        selected = user_selection[chat_id]["assets"]

        if asset in selected:
            selected.remove(asset)
        else:
            selected.append(asset)

        # show correct menu again
        if asset in CRYPTO_LIST:

            query.message.edit_text(
                "Select Crypto Assets:",
                reply_markup=crypto_list_menu(selected)
            )

        else:

            query.message.edit_text(
                "Select Forex Assets:",
                reply_markup=forex_list_menu(selected)
            )

    # =====================================================
    # SAVE ASSETS
    # =====================================================

    elif data == "done_assets":

        selected = user_selection[chat_id]["assets"]

        update_user(chat_id, {
            "assets": selected
        })

        text = "✅ Assets Saved\n\n"

        if selected:
            text += "\n".join(selected)
        else:
            text += "No assets selected"

        query.message.edit_text(
            text,
            reply_markup=main_menu()
        )

    # =====================================================
    # SETTINGS
    # =====================================================

    elif data == "settings":

        query.message.edit_text(
            "⚙ Settings",
            reply_markup=settings_menu()
        )

    # =====================================================
    # INTERVAL SETTINGS
    # =====================================================

    elif data == "interval_settings":

        query.message.edit_text(
            "Choose alert interval:",
            reply_markup=interval_menu()
        )

    elif data.startswith("interval_"):

        minutes = int(data.split("_")[1])

        update_user(chat_id, {
            "interval": minutes
        })

        query.message.edit_text(
            f"✅ Alert interval set to {minutes} mins",
            reply_markup=main_menu()
        )

    # =====================================================
    # CONDITION SETTINGS
    # =====================================================

    elif data == "condition_settings":

        user = get_user(chat_id)

        if not user:

            query.message.edit_text(
                "User data not found."
            )

            return

        #assets = user.get("assets", [])
        #user = get_user(chat_id)

       # assets = user.get("assets", {})
        print(user.data.get("assets",[]))
        assets = user.data.get("assets", [])
        #assets = user.get("assets", [])
       # assets = user.data.assets
        print(assets)

        if not assets:

            query.message.edit_text(
                "⚠ No assets selected yet.\n\nPlease select assets first.",
                reply_markup=asset_menu()
            )

            return

        query.message.edit_text(
            "Select asset:",
            reply_markup=condition_asset_menu(assets)
        )

    # =====================================================
    # CONDITION ASSET
    # =====================================================

    elif data.startswith("cond_asset_"):

        asset = data.split("_")[2]

        user = get_user(chat_id)

        #conditions = user.data.get("conditions", {})
        conditions = user.data.get("conditions") or {}

        asset_conditions = conditions.data.get(asset) or []

        query.message.edit_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, asset_conditions)
        )

    # =====================================================
    # ADD CONDITION
    # =====================================================

    elif data.startswith("addcond_"):

        asset = data.split("_")[1]

        query.message.edit_text(
            f"{asset} - Choose condition type:",
            reply_markup=add_condition_type_menu(asset)
        )

    # =====================================================
    # ADD CONDITION TYPE
    # =====================================================

    elif data.startswith("addtype_"):

        parts = data.split("_")

        asset = parts[1]
        cond_type = parts[2]

        user = get_user(chat_id)

        #conditions = user.data.get("conditions", {})
        conditions = user.data.get("conditions") or {}

        if asset not in conditions:
            conditions[asset] = []

        new_condition = {
            "id": str(uuid.uuid4())[:6],
            "type": cond_type,
            "value": 2
        }

        conditions[asset].append(new_condition)

        update_user(chat_id, {
            "conditions": conditions
        })

        query.message.edit_text(
            f"✅ Added condition for {asset}",
            reply_markup=condition_list_menu(
                asset,
                conditions[asset]
            )
        )

    # =====================================================
    # REMOVE CONDITION MENU
    # =====================================================

    elif data.startswith("removecond_"):

        asset = data.split("_")[1]

        user = get_user(chat_id)

        #conditions = user.data.get("conditions", {})
        conditions = user.data.get("conditions") or {}

        asset_conditions = conditions.get(asset, [])

        query.message.edit_text(
            f"Remove condition for {asset}:",
            reply_markup=remove_condition_menu(
                asset,
                asset_conditions
            )
        )

    # =====================================================
    # DELETE CONDITION
    # =====================================================

    elif data.startswith("delcond_"):

        parts = data.split("_")

        asset = parts[1]
        cond_id = parts[2]

        user = get_user(chat_id)

        #conditions = user.data.get("conditions", {})
        conditions = user.data.get("conditions") or {}

        if asset in conditions:

            conditions[asset] = [
                c for c in conditions[asset]
                if c["id"] != cond_id
            ]

        update_user(chat_id, {
            "conditions": conditions
        })

        query.message.edit_text(
            f"✅ Condition removed from {asset}",
            reply_markup=condition_list_menu(
                asset,
                conditions.get(asset, [])
            )
        )

    # =====================================================
    # CHECK TOP MOVERS
    # =====================================================

    elif data == "check_top":

        crypto = get_top_movers("crypto")
        forex = get_top_movers("forex")

        text = "📈 TOP CRYPTO\n\n"

        for coin, value in crypto:
            text += f"{coin} increasing by {value}% every 30 mins\n"

        text += "\n💱 TOP FOREX\n\n"

        for pair, value in forex:
            text += f"{pair} increasing by {value}% every 30 mins\n"

        query.message.edit_text(text)

    # =====================================================
    # UPGRADE
    # =====================================================

    elif data == "upgrade":

        query.message.edit_text(
            "Choose a plan:",
            reply_markup=upgrade_menu()
        )

    # =====================================================
    # BACK MAIN
    # =====================================================

    elif data == "back_main":

        query.message.edit_text(
            "Main Menu",
            reply_markup=main_menu()
        )

# =========================================================
# ERROR HANDLER
# =========================================================

def error_handler(update, context):

    print("ERROR:")
    print(traceback.format_exc(), flush=True)

# =========================================================
# HANDLERS
# =========================================================

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("menu", menu))

dp.add_handler(
    CallbackQueryHandler(button)
)

dp.add_error_handler(error_handler)

# =========================================================
# START POLLING
# =========================================================

updater.start_polling(
    drop_pending_updates=True,
    allowed_updates=["message", "callback_query"]
)

print("BOT RUNNING...", flush=True)

updater.idle()
