from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Update
from ui import main_menu, asset_menu, upgrade_menu
from appwrite_client import db
import config, time

updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher
updater.start_polling(drop_pending_updates=True)

# START
def start(update, context):
    chat_id = str(update.message.chat_id)

    # Try to create user if not exists
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

    # Handle payment activation
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

    # Show UI
    update.message.reply_text(
        "Welcome 👋\n\nTrack market moves easily.",
        reply_markup=main_menu()
    )


# BUTTON HANDLER
def button(update, context):
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


dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
