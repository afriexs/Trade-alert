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

    # Strong list (global + Nigerian interest)
    symbols = [
        "AAPL","TSLA","MSFT","AMZN","NVDA",
        "META","GOOGL","NFLX","INTC","AMD",
        "BABA","SHOP","UBER","PYPL","V",
        "MA","JPM","WMT","DIS","KO",
        "PEP","PFE","MRNA","XOM","CVX",
        "BA","GM","F","SNAP","T",
        "VZ","ADBE","CRM","ORCL","IBM",
        "SQ","COIN","ROKU"
    ]

    url = "https://query1.finance.yahoo.com/v7/finance/quote"

    stock_data = {}

    try:
        response = requests.get(url, params={
            "symbols": ",".join(symbols)
        }).json()

        results = response.get("quoteResponse", {}).get("result", [])

        for item in results:
            symbol = item.get("symbol")
            price = item.get("regularMarketPrice")

            if symbol and price:
                stock_data[symbol] = float(price)

    except Exception as e:
        print("❌ Yahoo error:", e)

    # Safety check
    if not stock_data:
        print("⚠️ No stock data retrieved — skipping save")
        return

    save_json("data/stocks.json", stock_data)
    print(f"✅ Stocks saved: {len(stock_data)}")

# ---------------- RUN ----------------
update_forex()
update_crypto()
update_stocks()
