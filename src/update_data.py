import requests, json

def update_forex():
    url = "https://latest.currency-api.pages.dev/v1/currencies/usd.json"
    data = requests.get(url).json()
    with open("data/forex.json", "w") as f:
        json.dump(data, f)

def update_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    data = requests.get(url).json()[:100]
    with open("data/crypto.json", "w") as f:
        json.dump(data, f)

def update_stocks():
    symbols = "aapl.us,tsla.us,msft.us"
    url = f"https://stooq.com/q/l/?s={symbols}&f=sd2t2ohlcv&h&e=json"
    data = requests.get(url).json()
    with open("data/stocks.json", "w") as f:
        json.dump(data, f)

update_forex()
update_crypto()
update_stocks()