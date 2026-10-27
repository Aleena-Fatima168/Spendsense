"""
report.py - Generates a professional PDF summary report using fpdf2.
"""

from datetime import datetime

import pandas as pd
from fpdf import FPDF

PRIMARY  = (79,  70, 229)
ACCENT   = (14, 165, 233)
SUCCESS  = (16, 185, 129)
WARNING  = (245, 158, 11)
DANGER   = (239, 68,  68)
DARK     = (30,  41,  59)
MUTED    = (100, 116, 139)
LIGHT_BG = (248, 250, 252)
WHITE    = (255, 255, 255)
BORDER   = (226, 232, 240)

CATEGORY_COLORS_RGB = {
    "Groceries":      SUCCESS,
    "Dining":         WARNING,
    "Transportation": ACCENT,
    "Shopping":       (139, 92, 246),
    "Entertainment":  DANGER,
    "Subscriptions":  (6, 182, 212),
    "Other":          MUTED,
}


def _safe(text: str) -> str:
    """Replace non-latin-1 characters so Helvetica does not crash."""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "*",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class FinanceReport(FPDF):
    def __init__(self, title="Personal Finance Report"):
        super().__init__()
        self.report_title = _safe(title)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def header(self):
        self.set_fill_color(*PRIMARY)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.set_y(4)
        self.cell(0, 6, self.report_title, align="C")
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        generated = datetime.now().strftime("%d %b %Y")
        self.cell(0, 6, f"Page {self.page_no()}  |  Generated {generated}", align="C")

    def section_title(self, text):
        self.ln(4)
        self.set_fill_color(*LIGHT_BG)
        self.set_draw_color(*BORDER)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*DARK)
        self.cell(0, 9, _safe(f"  {text}"), border="B", fill=True, ln=True)
        self.ln(3)

    def kpi_row(self, items):
        col_w = (self.w - 36) / len(items)
        for label, value in items:
            x, y = self.get_x(), self.get_y()
            self.set_fill_color(*LIGHT_BG)
            self.set_draw_color(*BORDER)
            self.rect(x, y, col_w - 3, 22, "FD")
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*MUTED)
            self.set_xy(x + 3, y + 3)
            self.cell(col_w - 9, 5, _safe(label.upper()))
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*PRIMARY)
            self.set_xy(x + 3, y + 9)
            self.cell(col_w - 9, 8, _safe(value))
            self.set_xy(x + col_w, y)
        self.ln(26)

    def table(self, headers, rows, col_widths):
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, _safe(f"  {h}"), fill=True)
        self.ln()

        self.set_font("Helvetica", "", 9)
        for i, row in enumerate(rows):
            self.set_fill_color(*(LIGHT_BG if i % 2 == 0 else WHITE))
            self.set_text_color(*DARK)
            for val, w in zip(row, col_widths):
                self.cell(w, 7, _safe(f"  {val}"), fill=True, border="B")
            self.ln()
        self.ln(3)

    def progress_bar(self, label, value, total, color):
        pct = min(value / total, 1.0) if total > 0 else 0
        bar_w = self.w - 36
        filled = bar_w * pct

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK)
        self.cell(60, 6, _safe(label))
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*color)
        self.cell(30, 6, f"${value:,.2f}")
        self.set_text_color(*MUTED)
        self.cell(0, 6, f"{pct * 100:.1f}%", ln=True)

        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*BORDER)
        self.rect(x, y, bar_w, 4, "F")
        if filled > 0:
            self.set_fill_color(*color)
            self.rect(x, y, filled, 4, "F")
        self.ln(7)


def generate_pdf(
    df_expenses: pd.DataFrame,
    df_income,
    category_totals: pd.DataFrame,
    insights: list,
    period: str,
) -> bytes:
    pdf = FinanceReport(title=f"Finance Report  |  {period}")
    pdf.add_page()

    total_spent  = df_expenses["amount"].sum()
    total_income = df_income["amount"].sum() if df_income is not None and not df_income.empty else 0
    savings      = total_income - total_spent
    n_tx         = len(df_expenses)
    avg_tx       = df_expenses["amount"].mean() if n_tx > 0 else 0

    pdf.section_title("Summary")
    pdf.kpi_row([
        ("Total Spent",     f"${total_spent:,.2f}"),
        ("Transactions",    str(n_tx)),
        ("Avg Transaction", f"${avg_tx:,.2f}"),
        ("Total Income",    f"${total_income:,.2f}" if total_income else "N/A"),
        ("Net Savings",     f"${savings:,.2f}"      if total_income else "N/A"),
    ])

    pdf.section_title("Spending by Category")
    cat_totals = (
        category_totals.groupby("category")["total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    for _, row in cat_totals.iterrows():
        color = CATEGORY_COLORS_RGB.get(row["category"], MUTED)
        pdf.progress_bar(row["category"], row["total"], total_spent, color)

    pdf.section_title("Insights")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*DARK)
    for insight in insights:
        pdf.set_x(18)
        pdf.multi_cell(0, 6, _safe(f"  *  {insight}"))
        pdf.ln(1)
    pdf.ln(2)

    pdf.section_title("Top 15 Transactions")
    top15 = df_expenses.nlargest(15, "amount")[
        ["date", "description", "amount", "predicted_category"]
    ]
    rows = [
        [
            str(r["date"])[:10],
            str(r["description"])[:28],
            f"${r['amount']:,.2f}",
            str(r["predicted_category"]),
        ]
        for _, r in top15.iterrows()
    ]
    pdf.table(
        headers=["Date", "Merchant", "Amount", "Category"],
        rows=rows,
        col_widths=[30, 72, 30, 40],
    )

    if df_income is not None and not df_income.empty:
        pdf.add_page()
        pdf.section_title("Income Records")
        income_rows = [
            [str(r["date"])[:10], str(r["description"])[:50], f"${r['amount']:,.2f}"]
            for _, r in df_income.iterrows()
        ]
        pdf.table(
            headers=["Date", "Source", "Amount"],
            rows=income_rows,
            col_widths=[30, 102, 40],
        )

    return bytes(pdf.output())
