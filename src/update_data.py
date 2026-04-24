import requests, json, time
from rate_history import update_history

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump({
            "timestamp": int(time.time()),
            "base": "USD",
            "data": data
        }, f)


def update_forex():
    url = "https://latest.currency-api.pages.dev/v1/currencies/usd.json"
    res = requests.get(url).json()

    forex_data = {}
    for k, v in res.get("usd", {}).items():
        forex_data[k.upper()] = v

    save_json("data/forex.json", forex_data)
    update_history("data/forex.json", "forex")


def update_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    res = requests.get(url).json()

    crypto_data = {}
    for coin in res[:100]:
        symbol = coin["symbol"].upper()
        crypto_data[symbol] = coin["current_price"]

    save_json("data/crypto.json", crypto_data)
    update_history("data/crypto.json", "crypto")


update_forex()
update_crypto()
