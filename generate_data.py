import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

MERCHANTS = {
    "Groceries": ["Walmart", "Whole Foods", "Trader Joe's", "Kroger"],
    "Dining": ["McDonald's", "Starbucks", "Chipotle", "Pizza Hut", "Uber Eats"],
    "Transportation": ["Uber", "Shell Gas", "Lyft", "Metro Pass"],
    "Subscriptions": ["Netflix", "Spotify", "Amazon Prime", "iCloud"],
    "Shopping": ["Amazon", "Target", "Zara", "H&M"],
    "Entertainment": ["AMC Theatres", "Steam", "PlayStation Store", "Concert Tickets"],
}

AMOUNT_RANGE = {
    "Groceries": (15, 120),
    "Dining": (8, 60),
    "Transportation": (5, 50),
    "Subscriptions": (5, 20),
    "Shopping": (15, 200),
    "Entertainment": (10, 80),
}

WEIGHTS = {
    "Groceries": 25,
    "Dining": 25,
    "Transportation": 20,
    "Subscriptions": 4,
    "Shopping": 16,
    "Entertainment": 10,
}


def generate(months=6, per_month=60):
    rows = []
    start = date.today().replace(day=1) - timedelta(days=30 * months)
    categories = list(WEIGHTS.keys())
    weights = list(WEIGHTS.values())

    for i in range(months * per_month):
        day_offset = random.randint(0, months * 30)
        d = start + timedelta(days=day_offset)
        cat = random.choices(categories, weights)[0]
        merchant = random.choice(MERCHANTS[cat])
        low, high = AMOUNT_RANGE[cat]
        amount = round(random.uniform(low, high), 2)
        rows.append({
            "date": d,
            "description": merchant,
            "amount": amount,
            "true_category": cat,
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate()
    df.to_csv("transactions.csv", index=False)
    print(df.head(10))
    print(f"\nSaved {len(df)} transactions to transactions.csv")