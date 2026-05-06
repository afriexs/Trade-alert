from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import (
    main_menu, asset_menu, upgrade_menu, settings_menu,
    interval_menu, crypto_list_menu, forex_list_menu,
    condition_asset_menu, condition_list_menu,
    remove_condition_menu, add_condition_type_menu
)
from rate_history import get_top_movers
import config, time, traceback, os, json, uuid, requests

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

user_selection = {}

# ---------------- GOOGLE APPS SCRIPT HELPERS ----------------
def get_user(chat_id):
    try:
        res = requests.get(config.GAS_URL, params={
            "action": "get_user",
            "chat_id": chat_id
        })
        return res.json()
    except:
        return None

def create_user(chat_id):
    requests.post(config.GAS_URL, json={
        "action": "create_user",
        "chat_id": chat_id
    })

def update_user(chat_id, data):
    payload = {
        "action": "update_user",
        "chat_id": chat_id
    }
    payload.update(data)

    requests.post(config.GAS_URL, json=payload)

# ---------------- START ----------------
def start(update, context):
    chat_id = str(update.message.chat_id)

    user = get_user(chat_id)

    if not user:
        create_user(chat_id)

    update.message.reply_text(
        "Welcome 👋",
        reply_markup=main_menu()
    )

# ---------------- MENU ----------------
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

    if chat_id not in user_selection:
        user_selection[chat_id] = {"assets": []}

    data = query.data
    print("BUTTON CLICKED:", data, flush=True)

    # ---------------- ASSET FLOW ----------------
    if data == "select_assets":
        query.message.edit_text("Choose asset type:", reply_markup=asset_menu())

    elif data == "asset_crypto":
        selected = user_selection[chat_id]["assets"]
        query.message.edit_text("Select Crypto:", reply_markup=crypto_list_menu(selected))

    elif data == "asset_forex":
        selected = user_selection[chat_id]["assets"]
        query.message.edit_text("Select Forex:", reply_markup=forex_list_menu(selected))

    elif data.startswith("toggle_"):
        asset = data.split("_")[1]

        if asset in user_selection[chat_id]["assets"]:
            user_selection[chat_id]["assets"].remove(asset)
        else:
            user_selection[chat_id]["assets"].append(asset)

        selected = user_selection[chat_id]["assets"]

        if asset in ["BTC", "ETH", "DOGE", "SOL", "BNB"]:
            query.message.edit_text("Select Crypto:", reply_markup=crypto_list_menu(selected))
        else:
            query.message.edit_text("Select Forex:", reply_markup=forex_list_menu(selected))

    elif data == "done_assets":
        selected = user_selection[chat_id]["assets"]

        update_user(chat_id, {
            "assets": json.dumps(selected)
        })

        query.message.edit_text(
            f"✅ Saved Assets:\n\n{', '.join(selected) if selected else 'None'}",
            reply_markup=main_menu()
        )

    # ---------------- SETTINGS ----------------
    elif data == "settings":
        query.edit_message_text("Settings:", reply_markup=settings_menu())

    elif data == "interval_settings":
        query.edit_message_text("Choose interval:", reply_markup=interval_menu())

    elif data.startswith("interval_"):
        minutes = int(data.split("_")[1])

        update_user(chat_id, {"interval": minutes})

        query.edit_message_text(f"✅ Interval set to {minutes} mins", reply_markup=main_menu())

    # ---------------- CONDITIONS ----------------
    elif data == "condition_settings":
        user = get_user(chat_id)

        assets = json.loads(user.get("assets", "[]"))

        if not assets:
            query.edit_message_text(
                "⚠ Select assets first",
                reply_markup=asset_menu()
            )
            return

        query.edit_message_text("Select asset:", reply_markup=condition_asset_menu(assets))

    elif data.startswith("cond_asset_"):
        asset = data.split("_")[2]

        user = get_user(chat_id)
        conditions = json.loads(user.get("conditions", "{}")).get(asset, [])

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

        user = get_user(chat_id)
        conditions = json.loads(user.get("conditions", "{}"))

        new_cond = {
            "id": str(uuid.uuid4())[:6],
            "type": ctype,
            "value": 2
        }

        conditions.setdefault(asset, []).append(new_cond)

        update_user(chat_id, {
            "conditions": json.dumps(conditions)
        })

        query.edit_message_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, conditions[asset])
        )

    elif data.startswith("removecond_"):
        asset = data.split("_")[1]

        user = get_user(chat_id)
        conditions = json.loads(user.get("conditions", "{}")).get(asset, [])

        query.edit_message_text(
            f"Remove condition:",
            reply_markup=remove_condition_menu(asset, conditions)
        )

    elif data.startswith("delcond_"):
        _, asset, cid = data.split("_")

        user = get_user(chat_id)
        conditions = json.loads(user.get("conditions", "{}"))

        conditions[asset] = [c for c in conditions.get(asset, []) if c["id"] != cid]

        update_user(chat_id, {
            "conditions": json.dumps(conditions)
        })

        query.edit_message_text(
            f"{asset} Conditions:",
            reply_markup=condition_list_menu(asset, conditions.get(asset, []))
        )

    # ---------------- OTHER ----------------
    elif data == "upgrade":
        query.message.edit_text("Upgrade your plan:", reply_markup=upgrade_menu())

    elif data == "back_main":
        query.edit_message_text("Main Menu:", reply_markup=main_menu())

    elif data == "check_top":
        crypto = get_top_movers("crypto")
        forex = get_top_movers("forex")

        text = "📈 Top Crypto\n\n"
        for c, val in crypto:
            text += f"{c} ↑ +{val}%\n"

        text += "\n💱 Top Forex\n\n"
        for f, val in forex:
            text += f"{f} ↑ +{val}%\n"

        query.edit_message_text(text)

# ---------------- HANDLERS ----------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("menu", menu))
dp.add_handler(CallbackQueryHandler(button))

# ---------------- START ----------------
updater.start_polling(
    drop_pending_updates=True,
    allowed_updates=["message", "callback_query"]
)

updater.idle()
