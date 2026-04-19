import requests, json, time

# ---------------- SAVE HELPER ----------------
def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump({
            "timestamp": int(time.time()),
            "base": "USD",
            "data": data
        }, f)


# ---------------- FOREX ----------------
def update_forex():
    url = "https://latest.currency-api.pages.dev/v1/currencies/usd.json"
    res = requests.get(url).json()

    # extract only usd rates
    forex_data = {}

    for k, v in res.get("usd", {}).items():
        forex_data[k.upper()] = v

    save_json("data/forex.json", forex_data)


# ---------------- CRYPTO ----------------
def update_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    res = requests.get(url).json()

    crypto_data = {}

    for coin in res[:100]:  # top 100
        symbol = coin["symbol"].upper()
        price = coin["current_price"]
        crypto_data[symbol] = price

    save_json("data/crypto.json", crypto_data)

# ---------------- RUN ----------------
update_forex()
update_crypto()
