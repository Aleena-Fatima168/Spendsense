"""
recurring.py — Detects recurring transactions (subscriptions, regular bills).
A merchant is considered recurring if it appears in at least `min_months`
distinct calendar months with a consistent amount (within `tolerance`).
"""

import pandas as pd


def detect_recurring(
    df: pd.DataFrame,
    min_months: int = 2,
    tolerance: float = 0.10,
) -> pd.DataFrame:
    """
    Returns a DataFrame of likely recurring transactions with columns:
        description, avg_amount, occurrences, months_seen, frequency
    """
    if df.empty:
        return pd.DataFrame(
            columns=["description", "avg_amount", "occurrences", "months_seen", "frequency"]
        )

    work = df.copy()
    work["month"] = pd.to_datetime(work["date"]).dt.to_period("M")

    summary = (
        work.groupby("description")
        .agg(
            occurrences=("amount", "count"),
            avg_amount=("amount", "mean"),
            std_amount=("amount", "std"),
            months_seen=("month", "nunique"),
        )
        .reset_index()
    )

    summary["std_amount"] = summary["std_amount"].fillna(0)
    summary["cv"] = summary["std_amount"] / summary["avg_amount"].replace(0, 1)

    recurring = summary[
        (summary["months_seen"] >= min_months) & (summary["cv"] <= tolerance)
    ].copy()

    def frequency_label(row):
        if row["months_seen"] >= 3 and row["occurrences"] / row["months_seen"] >= 0.8:
            return "Monthly"
        if row["occurrences"] >= 2:
            return "Periodic"
        return "Occasional"

    recurring["frequency"] = recurring.apply(frequency_label, axis=1)
    recurring = recurring.sort_values("avg_amount", ascending=False)

    return recurring[["description", "avg_amount", "occurrences", "months_seen", "frequency"]]
