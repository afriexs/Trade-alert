import json, time
from appwrite_client import get_users
from telegram import Bot
import config

bot = Bot(config.TELEGRAM_TOKEN)

def load_crypto():
    with open("data/crypto.json") as f:
        return json.load(f)

def get_price(asset, data):
    for coin in data:
        if coin['symbol'].upper() == asset:
            return coin['current_price']
    return None

def main():
    users = get_users()
    data = load_crypto()

    for user in users:
        if user['expires_at'] < time.time():
            bot.send_message(user['chat_id'],
                "❌ Subscription expired", 
            )
            continue

        messages = []

        for asset in user['assets']:
            price = get_price(asset, data)
            if not price:
                continue

            ref = user['reference_prices'].get(asset, price)
            change = (price - ref)/ref

            if abs(change) >= user['threshold']:
                value = user['amount'] * (price/ref)

                messages.append(
                    f"{asset}: {round(change*100,2)}%\n"
                    f"₦{user['amount']} → ₦{round(value,2)}"
                )

        if messages:
            bot.send_message(user['chat_id'], "\n\n".join(messages))

main()