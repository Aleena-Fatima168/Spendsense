"""
database.py — SQLite persistence layer.
Stores transactions so users do not have to re-upload their CSV every session.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("finance.db")


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create tables if they do not exist yet."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                date               TEXT    NOT NULL,
                description        TEXT    NOT NULL,
                amount             REAL    NOT NULL,
                predicted_category TEXT,
                source             TEXT    DEFAULT 'upload'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT  NOT NULL,
                description TEXT  NOT NULL,
                amount      REAL  NOT NULL
            )
        """)
        conn.commit()


def save_transactions(df: pd.DataFrame, source: str = "upload") -> int:
    """
    Insert rows from a DataFrame into the transactions table.
    Skips exact duplicates (same date + description + amount).
    Returns the number of new rows inserted.
    """
    init_db()
    df = df.copy()
    df["source"] = source

    cols = ["date", "description", "amount", "predicted_category", "source"]
    for col in cols:
        if col not in df.columns:
            df[col] = None

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    with _connect() as conn:
        existing = pd.read_sql(
            "SELECT date, description, amount FROM transactions", conn
        )
        existing["amount"] = existing["amount"].astype(float)
        df["amount"] = df["amount"].astype(float)

        merged = df.merge(
            existing, on=["date", "description", "amount"], how="left", indicator=True
        )
        new_rows = df[merged["_merge"] == "left_only"]

        if not new_rows.empty:
            new_rows[cols].to_sql(
                "transactions", conn, if_exists="append", index=False
            )

    return len(new_rows)


def load_transactions() -> pd.DataFrame:
    """Load all transactions from the database."""
    init_db()
    with _connect() as conn:
        df = pd.read_sql(
            "SELECT * FROM transactions ORDER BY date ASC", conn, parse_dates=["date"]
        )
    return df


def save_income(df: pd.DataFrame) -> int:
    """Insert income rows. Returns number of new rows inserted."""
    init_db()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    with _connect() as conn:
        existing = pd.read_sql("SELECT date, description, amount FROM income", conn)
        existing["amount"] = existing["amount"].astype(float)
        df["amount"] = df["amount"].astype(float)

        merged = df.merge(
            existing, on=["date", "description", "amount"], how="left", indicator=True
        )
        new_rows = df[merged["_merge"] == "left_only"]

        cols = ["date", "description", "amount"]
        if not new_rows.empty:
            new_rows[cols].to_sql("income", conn, if_exists="append", index=False)

    return len(new_rows)


def load_income() -> pd.DataFrame:
    """Load all income rows from the database."""
    init_db()
    with _connect() as conn:
        df = pd.read_sql(
            "SELECT * FROM income ORDER BY date ASC", conn, parse_dates=["date"]
        )
    return df


def clear_transactions() -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM transactions")
        conn.commit()


def clear_income() -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM income")
        conn.commit()
