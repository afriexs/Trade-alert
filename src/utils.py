def parse_setup(text):
    try:
        parts = text.split()

        asset = parts[1].upper()
        amount = float(parts[2])
        price = float(parts[3])

        return {
            "asset": asset,
            "amount": amount,
            "price": price
        }
    except:
        return None


def format_money(value):
    return f"{round(value, 2):,}"


def percent_change(current, reference):
    return (current - reference) / reference