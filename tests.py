"""
tests.py — Unit tests for the Finance Analyzer.
Run with:  pytest tests.py -v
"""

import pandas as pd
import pytest

from analyze import generate_insights, monthly_category_totals
from categorize import categorize_with_rules
from recurring import detect_recurring


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "date": pd.to_datetime([
            "2026-06-01", "2026-06-05", "2026-06-10",
            "2026-07-01", "2026-07-05", "2026-07-10",
        ]),
        "description": [
            "Walmart", "McDonald's", "Amazon",
            "Walmart", "Starbucks", "Amazon",
        ],
        "amount": [50.0, 15.0, 120.0, 55.0, 12.0, 130.0],
        "predicted_category": [
            "Groceries", "Dining", "Shopping",
            "Groceries", "Dining", "Shopping",
        ],
    })


@pytest.fixture
def sample_totals(sample_transactions):
    df = sample_transactions.copy()
    df["month"] = df["date"].dt.to_period("M")
    return monthly_category_totals(df)


# ── categorize_with_rules ─────────────────────────────────────────────────────
class TestCategorizeWithRules:
    def test_groceries(self):
        assert categorize_with_rules("Walmart") == "Groceries"
        assert categorize_with_rules("Whole Foods") == "Groceries"
        assert categorize_with_rules("Kroger") == "Groceries"
        assert categorize_with_rules("Trader Joe's") == "Groceries"

    def test_dining(self):
        assert categorize_with_rules("McDonald's") == "Dining"
        assert categorize_with_rules("Starbucks") == "Dining"
        assert categorize_with_rules("Chipotle") == "Dining"
        assert categorize_with_rules("Pizza Hut") == "Dining"
        assert categorize_with_rules("Uber Eats") == "Dining"

    def test_transportation(self):
        assert categorize_with_rules("Uber") == "Transportation"
        assert categorize_with_rules("Lyft") == "Transportation"
        assert categorize_with_rules("Shell Gas") == "Transportation"
        assert categorize_with_rules("Metro Pass") == "Transportation"

    def test_subscriptions(self):
        assert categorize_with_rules("Netflix") == "Subscriptions"
        assert categorize_with_rules("Spotify") == "Subscriptions"
        assert categorize_with_rules("Amazon Prime") == "Subscriptions"
        assert categorize_with_rules("iCloud") == "Subscriptions"

    def test_shopping(self):
        assert categorize_with_rules("Amazon") == "Shopping"
        assert categorize_with_rules("Target") == "Shopping"
        assert categorize_with_rules("Zara") == "Shopping"
        assert categorize_with_rules("H&M") == "Shopping"

    def test_entertainment(self):
        assert categorize_with_rules("AMC Theatres") == "Entertainment"
        assert categorize_with_rules("Steam") == "Entertainment"
        assert categorize_with_rules("PlayStation Store") == "Entertainment"
        assert categorize_with_rules("Concert Tickets") == "Entertainment"

    def test_unknown_returns_none(self):
        assert categorize_with_rules("Joe's Corner Cafe") is None
        assert categorize_with_rules("Local Pharmacy") is None

    def test_case_insensitive(self):
        assert categorize_with_rules("WALMART") == "Groceries"
        assert categorize_with_rules("mcdonald's") == "Dining"


# ── monthly_category_totals ───────────────────────────────────────────────────
class TestMonthlyCategoryTotals:
    def test_returns_dataframe(self, sample_transactions):
        df = sample_transactions.copy()
        df["month"] = df["date"].dt.to_period("M")
        result = monthly_category_totals(df)
        assert isinstance(result, pd.DataFrame)

    def test_columns(self, sample_totals):
        assert set(sample_totals.columns) == {"month", "category", "total"}

    def test_totals_correct(self, sample_totals):
        jun_groceries = sample_totals[
            (sample_totals["month"].astype(str) == "2026-06") &
            (sample_totals["category"] == "Groceries")
        ]["total"].values[0]
        assert jun_groceries == pytest.approx(50.0)

    def test_no_negative_totals(self, sample_totals):
        assert (sample_totals["total"] >= 0).all()


# ── generate_insights ─────────────────────────────────────────────────────────
class TestGenerateInsights:
    def test_returns_list(self, sample_totals):
        result = generate_insights(sample_totals)
        assert isinstance(result, list)

    def test_at_least_one_insight(self, sample_totals):
        result = generate_insights(sample_totals)
        assert len(result) >= 1

    def test_single_month_message(self):
        single = pd.DataFrame({
            "month": pd.period_range("2026-06", periods=1, freq="M"),
            "category": ["Groceries"],
            "total": [100.0],
        })
        result = generate_insights(single)
        assert len(result) == 1
        assert "two months" in result[0] or "2 months" in result[0]

    def test_insights_are_strings(self, sample_totals):
        for insight in generate_insights(sample_totals):
            assert isinstance(insight, str)


# ── detect_recurring ──────────────────────────────────────────────────────────
class TestDetectRecurring:
    def test_detects_monthly_merchant(self, sample_transactions):
        result = detect_recurring(sample_transactions, min_months=2, tolerance=0.10)
        assert "Walmart" in result["description"].values

    def test_columns_present(self, sample_transactions):
        result = detect_recurring(sample_transactions)
        expected = {"description", "avg_amount", "occurrences", "months_seen", "frequency"}
        assert expected.issubset(set(result.columns))

    def test_empty_input(self):
        empty = pd.DataFrame(columns=["date", "description", "amount"])
        result = detect_recurring(empty)
        assert result.empty

    def test_single_occurrence_not_recurring(self):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-06-01"]),
            "description": ["One Time Shop"],
            "amount": [99.0],
        })
        result = detect_recurring(df, min_months=2)
        assert "One Time Shop" not in result["description"].values
