from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Select Assets", callback_data="select_assets")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
        [InlineKeyboardButton("📈 Check Rate", callback_data="check_rate")],
        [InlineKeyboardButton("💳 Upgrade Plan", callback_data="upgrade")]
    ])

def asset_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Crypto", callback_data="asset_crypto")],
        [InlineKeyboardButton("Forex", callback_data="asset_forex")],
        [InlineKeyboardButton("✅ Done", callback_data="done_assets")]
    ])

def upgrade_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Standard Plan", url="YOUR_SELAR_LINK")],
        [InlineKeyboardButton("Premium Plan", url="YOUR_SELAR_LINK")]
    ])
