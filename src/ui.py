from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Select Assets", callback_data="select_assets")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
        [InlineKeyboardButton("📈 Check Top 10", callback_data="check_top")],
        [InlineKeyboardButton("💳 Upgrade Plan", callback_data="upgrade")]
    ])

def asset_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Crypto", callback_data="asset_crypto")],
        [InlineKeyboardButton("Forex", callback_data="asset_forex")],
        [InlineKeyboardButton("Both", callback_data="asset_both")],
        [InlineKeyboardButton("✅ Done", callback_data="done_assets")]
    ])

def settings_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ Interval Alerts", callback_data="interval_settings")],
        [InlineKeyboardButton("🎯 Condition Alerts", callback_data="condition_settings")],
        [InlineKeyboardButton("⬅ Back", callback_data="back_main")]
    ])

def interval_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 Hour", callback_data="interval_60")],
        [InlineKeyboardButton("2 Hours", callback_data="interval_120")],
        [InlineKeyboardButton("4 Hours", callback_data="interval_240")]
    ])

def upgrade_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Standard Plan", url="YOUR_SELAR_LINK")],
        [InlineKeyboardButton("Premium Plan", url="YOUR_SELAR_LINK")]
    ])
