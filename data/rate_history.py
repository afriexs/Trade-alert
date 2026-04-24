import json, time, os

DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

MAX_POINTS = 4  # last 4 intervals


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)


def update_history(source_file, asset_type):
    with open(source_file, "r") as f:
        new_data = json.load(f)["data"]

    history = load_history()

    if asset_type not in history:
        history[asset_type] = {}

    for asset, price in new_data.items():
        if asset not in history[asset_type]:
            history[asset_type][asset] = []

        history[asset_type][asset].append(price)

        # keep only last 4
        if len(history[asset_type][asset]) > MAX_POINTS:
            history[asset_type][asset].pop(0)

    save_history(history)


def get_top_movers(asset_type):
    history = load_history().get(asset_type, {})
    movers = []

    for asset, prices in history.items():
        if len(prices) < 2:
            continue

        change = ((prices[-1] - prices[0]) / prices[0]) * 100

        if change > 0:
            movers.append((asset, round(change, 2)))

    movers.sort(key=lambda x: x[1], reverse=True)

    return movers[:5]
