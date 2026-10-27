import pandas as pd

# Keyword rules: if a merchant name contains a keyword, assign that category
RULES = {
    "Groceries":      ["walmart", "whole foods", "trader joe", "kroger"],
    "Dining":         ["mcdonald", "starbucks", "chipotle", "pizza hut", "uber eats"],
    "Transportation": ["uber", "shell", "lyft", "metro"],
    "Subscriptions":  ["netflix", "spotify", "amazon prime", "icloud"],
    "Shopping":       ["amazon", "target", "zara", "h&m"],
    "Entertainment":  ["amc", "steam", "playstation", "concert"],
}


def categorize_with_rules(description: str) -> str | None:
    desc_lower = description.lower()
    for category, keywords in RULES.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return None  # no rule matched


def main():
    df = pd.read_csv("transactions.csv")
    df["predicted_category"] = df["description"].apply(categorize_with_rules)
    df["source"] = df["predicted_category"].apply(
        lambda x: "rules" if pd.notna(x) else None
    )

    mask = df["predicted_category"].isna()
    unmatched = df.loc[mask, "description"].unique().tolist()

    if unmatched:
        print(f"{len(unmatched)} merchants did not match any rule. Sending to LLM:")
        print(unmatched)

        from llm_categorize import categorize_with_llm

        llm_result = categorize_with_llm(unmatched)
        df.loc[mask, "predicted_category"] = df.loc[mask, "description"].map(llm_result)
        df.loc[mask, "source"] = "llm"
    else:
        print("All transactions categorized by rules. LLM was not needed.")

    print("\nCategorization source breakdown:")
    print(df["source"].value_counts())

    df.to_csv("transactions_categorized.csv", index=False)
    print("\nSaved: transactions_categorized.csv")


if __name__ == "__main__":
    main()
