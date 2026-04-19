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


# ---------------- STOCKS ----------------
def update_stocks():
    # Expanded list (popular globally + Nigerian interest)
    symbols = [
        "aapl.us","tsla.us","msft.us","amzn.us","nvda.us",
        "meta.us","googl.us","nflx.us","intel.us","amd.us",
        "baba.us","shop.us","uber.us","lyft.us","pypl.us",
        "visa.us","ma.us","jpm.us","wmt.us","dis.us",
        "ko.us","pepsi.us","pfe.us","mrna.us","xom.us",
        "cvx.us","ba.us","gm.us","f.us","snap.us",
        "t.us","vzw.us","adbe.us","crm.us","orcl.us",
        "ibm.us","sq.us","block.us","coin.us","roku.us"
    ]

    # split into chunks (stooq limit)
    stock_data = {}

    for i in range(0, len(symbols), 10):
        chunk = ",".join(symbols[i:i+10])
        url = f"https://stooq.com/q/l/?s={chunk}&f=sd2t2ohlcv&h&e=json"

        try:
            res = requests.get(url).json()

            for item in res.get("symbols", []):
                sym = item["symbol"].split(".")[0].upper()
                price = float(item.get("close", 0))

                if price > 0:
                    stock_data[sym] = price

        except:
            continue

    save_json("data/stocks.json", stock_data)


# ---------------- RUN ----------------
update_forex()
update_crypto()
update_stocks()
