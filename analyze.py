import pandas as pd


def load_data(path="transactions_categorized.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df


def monthly_category_totals(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["month", "predicted_category"])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"predicted_category": "category", "amount": "total"})
    )


def generate_insights(totals: pd.DataFrame) -> list[str]:
    insights = []
    months = sorted(totals["month"].unique())

    if len(months) < 2:
        return ["At least two months of data are needed to generate insights."]

    latest, previous = months[-1], months[-2]

    latest_df = totals[totals["month"] == latest].set_index("category")["total"]
    prev_df = totals[totals["month"] == previous].set_index("category")["total"]

    for category in latest_df.index:
        latest_amt = latest_df.get(category, 0)
        prev_amt = prev_df.get(category, 0)

        if prev_amt == 0:
            continue

        pct_change = ((latest_amt - prev_amt) / prev_amt) * 100

        if abs(pct_change) >= 10:
            direction = "more" if pct_change > 0 else "less"
            insights.append(
                f"You spent {abs(pct_change):.0f}% {direction} on {category} "
                f"than last month ({latest}): ${latest_amt:.2f} vs ${prev_amt:.2f}"
            )

    total_latest = latest_df.sum()
    top_category = latest_df.idxmax()
    top_pct = (latest_df[top_category] / total_latest) * 100
    insights.append(
        f"In {latest}, your highest spending was on {top_category} "
        f"(${latest_df[top_category]:.2f}, {top_pct:.0f}% of the total)"
    )

    return insights


def main():
    df = load_data()
    totals = monthly_category_totals(df)

    print("=== Monthly Category Totals ===")
    print(totals.to_string(index=False))

    print("\n=== Insights ===")
    for insight in generate_insights(totals):
        print(f"- {insight}")


if __name__ == "__main__":
    main()