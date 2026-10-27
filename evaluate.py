import pandas as pd


def evaluate(path: str = "transactions_categorized.csv") -> None:
    df = pd.read_csv(path)

    # Check required columns exist
    if "true_category" not in df.columns or "predicted_category" not in df.columns:
        print("Error: CSV must contain both 'true_category' and 'predicted_category' columns.")
        return

    df = df.dropna(subset=["true_category", "predicted_category"])
    total = len(df)

    if total == 0:
        print("No rows to evaluate.")
        return

    # ── Overall Accuracy ──────────────────────────────────────────────────────
    correct = (df["true_category"] == df["predicted_category"]).sum()
    accuracy = (correct / total) * 100

    print("=" * 50)
    print("  CATEGORIZATION EVALUATION REPORT")
    print("=" * 50)
    print(f"  Total Transactions : {total}")
    print(f"  Correctly Labeled  : {correct}")
    print(f"  Incorrectly Labeled: {total - correct}")
    print(f"  Overall Accuracy   : {accuracy:.1f}%")
    print("=" * 50)

    # ── Per-Category Accuracy ─────────────────────────────────────────────────
    print("\n  Accuracy by Category")
    print("-" * 50)
    print(f"  {'Category':<20} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
    print("-" * 50)

    for category in sorted(df["true_category"].unique()):
        cat_df = df[df["true_category"] == category]
        cat_correct = (cat_df["predicted_category"] == category).sum()
        cat_total = len(cat_df)
        cat_acc = (cat_correct / cat_total) * 100
        print(f"  {category:<20} {cat_correct:>8} {cat_total:>8} {cat_acc:>9.1f}%")

    print("-" * 50)

    # ── Misclassified Transactions ────────────────────────────────────────────
    misclassified = df[df["true_category"] != df["predicted_category"]]

    if misclassified.empty:
        print("\n  No misclassified transactions found.")
    else:
        print(f"\n  Misclassified Transactions ({len(misclassified)} total)")
        print("-" * 50)
        print(f"  {'Merchant':<25} {'True':<18} {'Predicted':<18}")
        print("-" * 50)
        for _, row in misclassified.iterrows():
            print(f"  {row['description']:<25} {row['true_category']:<18} {row['predicted_category']:<18}")
        print("-" * 50)

    print()


if __name__ == "__main__":
    evaluate()
