import pandas as pd
import plotly.express as px
import streamlit as st

from analyze import generate_insights, load_data, monthly_category_totals
from categorize import categorize_with_rules
from database import (
    clear_income, clear_transactions, init_db,
    load_income, load_transactions,
    save_income, save_transactions,
)
from recurring import detect_recurring
from report import generate_pdf

st.set_page_config(page_title="SpendSense | Finance Analyzer", layout="wide")

CORAL = "#c084fc"
RED = "#ff6b6b"
AMBER = "#ffc857"
ROSE = "#ec4899"
TEAL = "#2dd4bf"
GREEN = "#4ade80"
BG = "#0f0b1a"
PANEL = "#1a1428"

CATEGORY_COLORS = {
    "Groceries": "#4ade80",
    "Dining": "#ffc857",
    "Transportation": "#38bdf8",
    "Subscriptions": "#818cf8",
    "Shopping": "#ff6b9d",
    "Entertainment": "#2dd4bf",
    "Other": "#9ca3af",
}

WEEKDAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
REQUIRED_COLUMNS = {"date", "description", "amount"}

# ---------- Custom styling ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stMarkdown, .stDataFrame {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.3px;
}

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(168, 85, 247, 0.20), transparent 40%),
        radial-gradient(circle at 96% 6%, rgba(255, 200, 87, 0.14), transparent 38%),
        radial-gradient(circle at 55% 100%, rgba(236, 72, 153, 0.10), transparent 42%),
        #0f0b1a;
}

.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px; }

/* Scrollbar */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: #0f0b1a; }
::-webkit-scrollbar-thumb { background: linear-gradient(#a855f7, #ffc857); border-radius: 999px; }

/* Animations */
@keyframes rise {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes floaty {
    0%, 100% { transform: translateY(0) translateX(0); }
    50% { transform: translateY(-18px) translateX(10px); }
}
@keyframes flow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #171026 0%, #0f0b1a 100%);
    border-right: 1px solid rgba(168, 85, 247, 0.28);
}
.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 3px;
    background: linear-gradient(90deg, #ffc857, #e879f9, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-sub { font-size: 0.72rem; opacity: 0.55; letter-spacing: 2px; text-transform: uppercase; }
.side-title {
    font-size: 0.72rem; letter-spacing: 2px; text-transform: uppercase;
    color: #ffc857; margin: 18px 0 6px 0; font-weight: 600;
}
span[data-baseweb="tag"] {
    background: linear-gradient(90deg, #7e22ce, #be185d) !important;
    border-radius: 8px !important;
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, #2a0e4a, #5b21b6, #a21caf, #be185d, #2a0e4a);
    background-size: 300% 300%;
    animation: flow 14s ease infinite, rise 0.7s ease both;
    padding: 40px 44px;
    border-radius: 26px;
    margin-bottom: 28px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    box-shadow: 0 24px 70px rgba(168, 85, 247, 0.28);
}
.orb { position: absolute; border-radius: 50%; filter: blur(2px); animation: floaty 9s ease-in-out infinite; }
.orb.one { width: 260px; height: 260px; right: -60px; top: -90px;
    background: radial-gradient(circle, rgba(255,255,255,0.22), transparent 65%); }
.orb.two { width: 170px; height: 170px; right: 180px; bottom: -80px; animation-delay: -3s;
    background: radial-gradient(circle, rgba(255,200,87,0.40), transparent 65%); }
.orb.three { width: 120px; height: 120px; left: 46%; top: -40px; animation-delay: -6s;
    background: radial-gradient(circle, rgba(236,72,153,0.40), transparent 65%); }
.hero .eyebrow {
    font-size: 0.72rem; letter-spacing: 3.5px; text-transform: uppercase;
    color: #ffe08a; margin-bottom: 12px; position: relative; z-index: 1;
}
.hero h1 {
    margin: 0; font-size: 2.7rem; font-weight: 700; position: relative; z-index: 1; line-height: 1.15;
    background: linear-gradient(90deg, #ffffff, #f5d0fe 55%, #ffc857);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p { margin: 12px 0 22px 0; opacity: 0.85; font-size: 1.02rem; position: relative; z-index: 1; max-width: 560px; }
.badge {
    display: inline-block;
    padding: 7px 18px;
    border-radius: 999px;
    font-size: 0.78rem;
    margin-right: 10px;
    color: #fff;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.28);
    backdrop-filter: blur(10px);
    position: relative; z-index: 1;
}

/* Metric cards */
.mcard {
    position: relative;
    overflow: hidden;
    background: linear-gradient(160deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 20px;
    padding: 22px 24px 18px 24px;
    animation: rise 0.7s ease both;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.mcard::before {
    content: "";
    position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: var(--accent);
}
.mcard::after {
    content: "";
    position: absolute; right: -40px; top: -40px;
    width: 130px; height: 130px; border-radius: 50%;
    background: var(--accent);
    opacity: 0.13;
    filter: blur(14px);
}
.mcard:hover {
    transform: translateY(-5px);
    border-color: var(--accent);
    box-shadow: 0 16px 38px rgba(0, 0, 0, 0.5);
}
.mcard .label { font-size: 0.72rem; opacity: 0.6; letter-spacing: 1.7px; text-transform: uppercase; }
.mcard .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem; font-weight: 700; margin-top: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mcard .caption {
    font-size: 0.82rem; opacity: 0.62;
    margin-top: 14px; padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Section headings */
.section { display: flex; align-items: center; gap: 12px; margin: 6px 0 14px 0; }
.section .bar { width: 5px; height: 26px; border-radius: 4px; background: linear-gradient(#ffc857, #e879f9, #a855f7); }
.section .t { font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 600; }
.section .s { font-size: 0.82rem; opacity: 0.55; margin-left: 4px; }

/* Notice */
.notice {
    background: rgba(255, 200, 87, 0.08);
    border: 1px solid rgba(255, 200, 87, 0.22);
    border-left: 4px solid #ffc857;
    border-radius: 12px;
    padding: 11px 16px;
    margin-bottom: 14px;
    font-size: 0.86rem;
}

/* Budget tracker */
.budget {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 8px;
}
.budget .row { display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 12px; }
.budget .status { font-size: 0.86rem; margin-top: 12px; opacity: 0.8; }

/* Insights */
.insight {
    display: flex; align-items: center; gap: 14px;
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 15px 20px;
    margin-bottom: 11px;
    font-size: 0.94rem;
    animation: rise 0.6s ease both;
    transition: transform 0.2s ease, background 0.2s ease;
}
.insight:hover { transform: translateX(6px); background: rgba(255, 255, 255, 0.07); }
.insight .tag {
    flex-shrink: 0;
    font-size: 0.66rem; font-weight: 700; letter-spacing: 1.5px;
    padding: 6px 12px; border-radius: 8px;
}
.insight.up { box-shadow: inset 4px 0 0 #ff6b6b; }
.insight.down { box-shadow: inset 4px 0 0 #4ade80; }
.insight.top { box-shadow: inset 4px 0 0 #ffc857; }
.insight.note { box-shadow: inset 4px 0 0 #2dd4bf; }
.insight.up .tag { background: rgba(255, 107, 107, 0.18); color: #ff8a8a; }
.insight.down .tag { background: rgba(74, 222, 128, 0.18); color: #4ade80; }
.insight.top .tag { background: rgba(255, 200, 87, 0.18); color: #ffc857; }
.insight.note .tag { background: rgba(45, 212, 191, 0.18); color: #2dd4bf; }

/* Category rows */
.catrow { margin-bottom: 17px; }
.cathead { display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 8px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 9px; }
.track { background: rgba(255, 255, 255, 0.08); height: 9px; border-radius: 999px; overflow: hidden; }
.track.big { height: 12px; }
.fill { height: 100%; border-radius: 999px; }
.muted { opacity: 0.6; }

/* Chart containers */
div[data-testid="stPlotlyChart"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 20px;
    padding: 8px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: none; margin-bottom: 10px; }
.stTabs button[role="tab"] {
    background: rgba(255, 255, 255, 0.06);
    padding: 10px 26px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    height: auto;
}
.stTabs button[role="tab"] p { font-weight: 500; font-size: 0.95rem; }
.stTabs button[role="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #a855f7, #ec4899);
    border: none;
    box-shadow: 0 6px 22px rgba(168, 85, 247, 0.40);
}
.stTabs button[role="tab"][aria-selected="true"] p { color: #ffffff; font-weight: 700; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Buttons */
.stDownloadButton button {
    background: linear-gradient(90deg, #a855f7, #ec4899);
    border: none;
    color: #ffffff;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.55rem 1.3rem;
}
.stDownloadButton button:hover { filter: brightness(1.1); color: #ffffff; }

/* Footer */
.footer { text-align: center; opacity: 0.4; font-size: 0.78rem; margin-top: 40px; letter-spacing: 1px; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Helper functions ----------
def metric_card(label: str, value: str, caption: str, color: str):
    html = (
        f'<div class="mcard" style="--accent:{color};">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="caption">{caption}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def section(title: str, subtitle: str = ""):
    sub = f'<span class="s">{subtitle}</span>' if subtitle else ""
    st.markdown(
        f'<div class="section"><div class="bar"></div><div class="t">{title}</div>{sub}</div>',
        unsafe_allow_html=True,
    )


def notice(text: str):
    st.markdown(f'<div class="notice">{text}</div>', unsafe_allow_html=True)


def insight_card(text: str):
    css, tag = "note", "NOTE"
    if "than last month" in text and " more on " in text:
        css, tag = "up", "RISING"
    elif "than last month" in text and " less on " in text:
        css, tag = "down", "FALLING"
    elif "highest spending" in text:
        css, tag = "top", "TOP SPEND"

    html = f'<div class="insight {css}"><span class="tag">{tag}</span><span>{text}</span></div>'
    st.markdown(html, unsafe_allow_html=True)


def category_bar(cat: str, amount: float, pct: float):
    color = CATEGORY_COLORS.get(cat, "#9ca3af")
    html = (
        '<div class="catrow">'
        f'<div class="cathead"><span><span class="dot" style="background:{color};"></span>{cat}</span>'
        f'<span class="muted">${amount:,.2f} &nbsp;|&nbsp; {pct:.0f}%</span></div>'
        f'<div class="track"><div class="fill" style="width:{pct}%; background:linear-gradient(90deg, {color}66, {color});"></div></div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def budget_tracker(month: str, spent: float, budget: float):
    pct = spent / budget * 100
    if pct < 80:
        color = GREEN
        status = f"You are ${budget - spent:,.2f} under budget."
    elif pct <= 100:
        color = AMBER
        status = f"Careful: only ${budget - spent:,.2f} of your budget is left."
    else:
        color = RED
        status = f"You are ${spent - budget:,.2f} over budget."
    width = min(pct, 100)
    html = (
        '<div class="budget">'
        f'<div class="row"><span>{month}</span>'
        f'<span class="muted">${spent:,.2f} of ${budget:,.2f} &nbsp;|&nbsp; {pct:.0f}%</span></div>'
        f'<div class="track big"><div class="fill" style="width:{width}%; '
        f'background:linear-gradient(90deg, {color}66, {color});"></div></div>'
        f'<div class="status">{status}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def style_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#f5ebe6"),
        title_font=dict(family="Space Grotesk, sans-serif", size=18),
        margin=dict(l=14, r=14, t=58, b=14),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        hoverlabel=dict(bgcolor=PANEL, font_size=13),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
    return fig


def partial_months(df: pd.DataFrame) -> set:
    """Months at the start or end of the data that do not cover the whole month."""
    months = sorted(df["month"].unique())
    partial = set()
    if not months:
        return partial
    first, last = months[0], months[-1]
    if df["date"].min().day > 7:
        partial.add(str(first))
    if df["date"].max().day < last.days_in_month - 7:
        partial.add(str(last))
    return partial


def load_default() -> pd.DataFrame:
    try:
        return load_data()
    except FileNotFoundError:
        st.error(
            "transactions_categorized.csv was not found. Run `python generate_data.py` "
            "and then `python categorize.py`, or upload your own CSV from the sidebar."
        )
        st.stop()


def prepare_upload(raw: pd.DataFrame, negative_expenses: bool) -> pd.DataFrame:
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    missing = REQUIRED_COLUMNS - set(raw.columns)
    if missing:
        st.error(
            f"Your CSV is missing these columns: {', '.join(sorted(missing))}. "
            "It needs the columns: date, description, amount."
        )
        st.stop()

    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["description"] = df["description"].astype(str)

    bad = df["date"].isna() | df["amount"].isna()
    if bad.any():
        st.sidebar.warning(f"{int(bad.sum())} rows with an invalid date or amount were skipped.")
        df = df[~bad].copy()

    if negative_expenses:
        df = df[df["amount"] < 0].copy()
        df["amount"] = df["amount"].abs()

    if df.empty:
        st.error("No usable transactions were found in this file. Please check the CSV format.")
        st.stop()

    if "predicted_category" not in df.columns:
        df["predicted_category"] = (
            df["description"].apply(categorize_with_rules).fillna("Other")
        )
    df["month"] = df["date"].dt.to_period("M")
    return df


@st.cache_data(show_spinner=False)
def ai_categories(descriptions: tuple) -> dict:
    # Imported here so the API key is only needed when this feature is used
    from llm_categorize import categorize_with_llm

    items = list(descriptions)
    result = {}
    for i in range(0, len(items), 40):
        result.update(categorize_with_llm(items[i:i + 40]))
    return result


def apply_ai(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["predicted_category"] == "Other"
    unknown = sorted(df.loc[mask, "description"].unique().tolist())
    if not unknown:
        return df
    try:
        with st.spinner("Asking the AI to categorize unknown merchants..."):
            mapping = ai_categories(tuple(unknown))
        df.loc[mask, "predicted_category"] = (
            df.loc[mask, "description"].map(mapping).fillna("Other")
        )
    except Exception as e:
        st.sidebar.error(f"AI categorization failed: {e}")
    return df


# ---------- Sidebar ----------
init_db()

st.sidebar.markdown('<div class="brand">SPENDSENSE</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="brand-sub">Finance Analyzer</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="side-title">Data</div>', unsafe_allow_html=True)
uploaded = st.sidebar.file_uploader(
    "Upload your CSV (columns: date, description, amount)", type="csv"
)

if uploaded is not None:
    negative_expenses = st.sidebar.checkbox("My CSV lists expenses as negative amounts")
    use_ai = st.sidebar.checkbox(
        "Categorize unknown merchants with AI",
        help="Needs the GEMINI_API_KEY environment variable to be set before the dashboard starts.",
    )
    uploaded.seek(0)
    df = prepare_upload(pd.read_csv(uploaded), negative_expenses)
    if use_ai:
        df = apply_ai(df)
    n_saved = save_transactions(df)
    if n_saved > 0:
        st.sidebar.success(f"{n_saved} new transactions saved to database.")
else:
    db_df = load_transactions()
    if not db_df.empty:
        db_df["month"] = db_df["date"].dt.to_period("M")
        if "predicted_category" not in db_df.columns:
            db_df["predicted_category"] = (
                db_df["description"].apply(categorize_with_rules).fillna("Other")
            )
        df = db_df
    else:
        df = load_default()

# ── Income sidebar ────────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="side-title">Income</div>', unsafe_allow_html=True)
uploaded_income = st.sidebar.file_uploader(
    "Upload income CSV (columns: date, description, amount)",
    type="csv",
    key="income_upload",
)
if uploaded_income is not None:
    uploaded_income.seek(0)
    raw_income = pd.read_csv(uploaded_income)
    raw_income.columns = [str(c).strip().lower() for c in raw_income.columns]
    raw_income["date"]   = pd.to_datetime(raw_income["date"],   errors="coerce")
    raw_income["amount"] = pd.to_numeric(raw_income["amount"], errors="coerce")
    raw_income = raw_income.dropna(subset=["date", "amount"])
    n_inc = save_income(raw_income)
    if n_inc > 0:
        st.sidebar.success(f"{n_inc} income records saved.")

df_income = load_income()

if st.sidebar.button("Clear saved database", help="Removes all stored transactions and income."):
    clear_transactions()
    clear_income()
    st.sidebar.success("Database cleared.")
    st.rerun()

partial = partial_months(df)

st.sidebar.markdown('<div class="side-title">Filters</div>', unsafe_allow_html=True)
all_categories = sorted(df["predicted_category"].unique())
selected_categories = st.sidebar.multiselect(
    "Categories", all_categories, default=all_categories
)

all_months = sorted(df["month"].astype(str).unique())
selected_months = st.sidebar.multiselect("Months", all_months, default=all_months)

st.sidebar.markdown('<div class="side-title">Budget</div>', unsafe_allow_html=True)
budget = st.sidebar.number_input(
    "Monthly budget ($)",
    min_value=0,
    value=0,
    step=100,
    help="Leave at 0 to hide the budget tracker.",
)

df_cat = df[df["predicted_category"].isin(selected_categories)]
df_filtered = df_cat[df_cat["month"].astype(str).isin(selected_months)].copy()

# ---------- Hero ----------
if df_filtered.empty:
    date_badge = "No data"
    count_badge = "0 transactions"
else:
    date_badge = f"{df_filtered['date'].min():%d %b %Y} to {df_filtered['date'].max():%d %b %Y}"
    count_badge = f"{len(df_filtered)} transactions"

st.markdown(
    f"""
<div class="hero">
<div class="orb one"></div><div class="orb two"></div><div class="orb three"></div>
<div class="eyebrow">Personal Finance Analyzer</div>
<h1>See your money clearly.</h1>
<p>Smart categories, live trends and plain-language insights, all in one beautiful dashboard.</p>
<span class="badge">{date_badge}</span><span class="badge">{count_badge}</span>
</div>
""",
    unsafe_allow_html=True,
)

if df_filtered.empty:
    st.warning(
        "No transactions match the selected filters. "
        "Please select at least one category and one month in the sidebar."
    )
    st.stop()

totals_all = monthly_category_totals(df_cat)
totals_for_insights = totals_all[~totals_all["month"].astype(str).isin(partial)]
totals_filtered = monthly_category_totals(df_filtered)
cat_totals = totals_filtered.groupby("category", as_index=False)["total"].sum()
cat_totals = cat_totals.sort_values("total", ascending=False)
grand_total = cat_totals["total"].sum()
top_category = cat_totals.iloc[0]["category"]
top_share = cat_totals.iloc[0]["total"] / grand_total * 100

n_months = df_filtered["month"].nunique()
n_merchants = df_filtered["description"].nunique()
largest = df_filtered["amount"].max()

# ---------- Metric cards ----------
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card(
        "Total Spent",
        f"${grand_total:,.2f}",
        f"Across {n_months} month{'s' if n_months != 1 else ''}",
        AMBER,
    )
with c2:
    metric_card(
        "Transactions",
        f"{len(df_filtered)}",
        f"From {n_merchants} different merchants",
        ROSE,
    )
with c3:
    metric_card(
        "Avg Transaction",
        f"${df_filtered['amount'].mean():,.2f}",
        f"Largest single payment: ${largest:,.2f}",
        CORAL,
    )
with c4:
    metric_card(
        "Top Category",
        top_category,
        f"{top_share:.0f}% of your total spending",
        CATEGORY_COLORS.get(top_category, TEAL),
    )

st.write("")

# ---------- Income / Savings KPIs ----------
total_income  = df_income["amount"].sum() if not df_income.empty else 0
net_savings   = total_income - grand_total
savings_rate  = (net_savings / total_income * 100) if total_income > 0 else None

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Trends", "Transactions", "Income & Savings", "Recurring"])

with tab1:
    if budget > 0:
        complete_months = [m for m in all_months if m not in partial]
        section("Monthly budget", "Based on all categories")
        if complete_months:
            latest_complete = complete_months[-1]
            spent = df.loc[df["month"].astype(str) == latest_complete, "amount"].sum()
            budget_tracker(latest_complete, spent, float(budget))
        else:
            notice("There is no complete month in this data yet, so the budget tracker is hidden.")
        st.write("")

    section("Insights", "Auto-generated from your latest two complete months")
    if partial:
        notice(
            f"{', '.join(sorted(partial))} contains only part of a month, "
            "so it is left out of the insights below to keep the comparison fair."
        )
    for insight in generate_insights(totals_for_insights):
        insight_card(insight)

    st.write("")
    section("Where your money goes")
    left, right = st.columns(2)

    with left:
        fig_pie = px.pie(
            cat_totals,
            names="category",
            values="total",
            hole=0.68,
            title="Category Breakdown",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
        )
        fig_pie.update_traces(
            textinfo="none",
            marker=dict(line=dict(color=BG, width=4)),
            hovertemplate="%{label}<br>$%{value:,.2f} (%{percent})<extra></extra>",
        )
        fig_pie.add_annotation(
            text=f"<b>${grand_total:,.0f}</b><br><span style='font-size:12px'>total spent</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=24, family="Space Grotesk, sans-serif"),
        )
        st.plotly_chart(style_fig(fig_pie), use_container_width=True)

    with right:
        st.markdown("#### Category Summary")
        st.write("")
        for _, row in cat_totals.iterrows():
            pct = (row["total"] / grand_total) * 100
            category_bar(row["category"], row["total"], pct)
        other_count = int((df_filtered["predicted_category"] == "Other").sum())
        if other_count > 0:
            st.caption(
                f"{other_count} transactions are in 'Other'. Add keywords in categorize.py, "
                "or enable AI categorization for uploaded files, to reduce this."
            )

    st.write("")
    top_merchants = (
        df_filtered.groupby("description", as_index=False)["amount"]
        .sum()
        .nlargest(8, "amount")
    )
    fig_merchants = px.bar(
        top_merchants,
        x="amount",
        y="description",
        orientation="h",
        title="Top Merchants",
        color="amount",
        color_continuous_scale=[AMBER, CORAL, ROSE],
        text="amount",
    )
    fig_merchants.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}<br>$%{x:,.2f}<extra></extra>",
    )
    fig_merchants.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False,
    )
    fig_merchants.update_xaxes(title="Total ($)")
    fig_merchants.update_yaxes(title="")
    st.plotly_chart(style_fig(fig_merchants), use_container_width=True)

with tab2:
    totals_str = totals_filtered.copy()
    totals_str["month"] = totals_str["month"].astype(str)

    section("Monthly trends")
    partial_in_view = sorted(m for m in partial if m in set(totals_str["month"]))
    if partial_in_view:
        notice(
            f"{', '.join(partial_in_view)} contains only part of a month, "
            "so its totals look lower than the other months."
        )

    fig_bar = px.bar(
        totals_str,
        x="month",
        y="total",
        color="category",
        title="Monthly Spending by Category",
        barmode="stack",
        color_discrete_map=CATEGORY_COLORS,
    )
    fig_bar.update_xaxes(title="", type="category")
    fig_bar.update_yaxes(title="Total ($)")
    st.plotly_chart(style_fig(fig_bar), use_container_width=True)

    monthly_total = totals_str.groupby("month", as_index=False)["total"].sum()
    fig_line = px.line(
        monthly_total,
        x="month",
        y="total",
        markers=True,
        title="Total Spending Over Time",
        color_discrete_sequence=[AMBER],
    )
    fig_line.update_traces(
        fill="tozeroy", fillcolor="rgba(255, 200, 87, 0.14)",
        line=dict(width=3), marker=dict(size=9),
    )
    fig_line.update_xaxes(title="", type="category")
    fig_line.update_yaxes(title="Total ($)")
    st.plotly_chart(style_fig(fig_line), use_container_width=True)

    st.write("")
    section("Patterns", "When and where you spend the most")
    col_a, col_b = st.columns(2)

    with col_a:
        weekday_sums = (
            df_filtered.groupby(df_filtered["date"].dt.dayofweek)["amount"]
            .sum()
            .reindex(range(7), fill_value=0)
        )
        weekday_df = pd.DataFrame({"weekday": WEEKDAYS_SHORT, "amount": weekday_sums.values})
        busiest = WEEKDAYS_FULL[int(weekday_sums.values.argmax())]
        fig_week = px.bar(
            weekday_df,
            x="weekday",
            y="amount",
            title=f"Spending by Day of the Week (busiest: {busiest})",
            color="amount",
            color_continuous_scale=[CORAL, ROSE],
            text="amount",
        )
        fig_week.update_traces(
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_week.update_layout(coloraxis_showscale=False)
        fig_week.update_xaxes(title="", tickangle=0)
        fig_week.update_yaxes(title="Total ($)")
        st.plotly_chart(style_fig(fig_week), use_container_width=True)

    with col_b:
        pivot = totals_str.pivot_table(
            index="category", columns="month", values="total",
            aggfunc="sum", fill_value=0,
        )
        fig_heat = px.imshow(
            pivot,
            aspect="auto",
            text_auto=".0f",
            title="Category by Month Heatmap",
            color_continuous_scale=[[0, PANEL], [0.5, CORAL], [1, AMBER]],
        )
        fig_heat.update_layout(coloraxis_showscale=False)
        fig_heat.update_xaxes(title="", type="category")
        fig_heat.update_yaxes(title="")
        st.plotly_chart(style_fig(fig_heat), use_container_width=True)

with tab3:
    section("All transactions")
    f1, f2 = st.columns([2, 1])
    with f1:
        query = st.text_input(
            "Search merchant", placeholder="Type a merchant name, for example Starbucks"
        )
    with f2:
        sort_by = st.selectbox(
            "Sort by", ["Newest first", "Oldest first", "Highest amount", "Lowest amount"]
        )

    view = df_filtered[["date", "description", "amount", "predicted_category"]].copy()
    if query:
        view = view[view["description"].str.contains(query, case=False, na=False)]

    if sort_by == "Newest first":
        view = view.sort_values("date", ascending=False)
    elif sort_by == "Oldest first":
        view = view.sort_values("date", ascending=True)
    elif sort_by == "Highest amount":
        view = view.sort_values("amount", ascending=False)
    else:
        view = view.sort_values("amount", ascending=True)

    st.caption(f"Showing {len(view)} of {len(df_filtered)} transactions")
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "description": "Merchant",
            "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            "predicted_category": "Category",
        },
    )
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Download filtered data (CSV)",
            view.to_csv(index=False).encode("utf-8"),
            file_name="filtered_transactions.csv",
            mime="text/csv",
        )
    with dl2:
        period_str = (
            f"{df_filtered['date'].min():%b %Y} - {df_filtered['date'].max():%b %Y}"
            if not df_filtered.empty else "All time"
        )
        pdf_bytes = generate_pdf(
            df_expenses=df_filtered,
            df_income=df_income if not df_income.empty else None,
            category_totals=totals_filtered,
            insights=generate_insights(totals_for_insights),
            period=period_str,
        )
        st.download_button(
            "Download PDF Report",
            pdf_bytes,
            file_name="finance_report.pdf",
            mime="application/pdf",
        )

# ── Tab 4: Income & Savings ───────────────────────────────────────────────────
with tab4:
    section("Income & Savings", "Upload an income CSV from the sidebar to populate this tab")

    if df_income.empty:
        notice(
            "No income data found. Upload an income CSV (columns: date, description, amount) "
            "from the sidebar to see your savings rate and net balance."
        )
    else:
        i1, i2, i3 = st.columns(3)
        with i1:
            metric_card("Total Income",  f"${total_income:,.2f}",
                        f"From {df_income['description'].nunique()} sources", GREEN)
        with i2:
            metric_card("Total Expenses", f"${grand_total:,.2f}",
                        f"Across {n_months} month{'s' if n_months != 1 else ''}", RED)
        with i3:
            sr_caption = f"{savings_rate:.1f}% of income saved" if savings_rate is not None else "N/A"
            metric_card(
                "Net Savings",
                f"${net_savings:,.2f}",
                sr_caption,
                GREEN if net_savings >= 0 else RED,
            )

        st.write("")
        section("Monthly Income vs Expenses")

        inc_monthly = (
            df_income.assign(month=pd.to_datetime(df_income["date"]).dt.to_period("M"))
            .groupby("month")["amount"].sum()
            .reset_index()
            .rename(columns={"amount": "total"})
        )
        inc_monthly["type"] = "Income"
        exp_monthly = (
            df_filtered.groupby("month")["amount"].sum()
            .reset_index()
            .rename(columns={"amount": "total"})
        )
        exp_monthly["type"] = "Expenses"

        inc_monthly["month"] = inc_monthly["month"].astype(str)
        exp_monthly["month"] = exp_monthly["month"].astype(str)
        combined = pd.concat([inc_monthly, exp_monthly], ignore_index=True)

        fig_inc = px.bar(
            combined, x="month", y="total", color="type", barmode="group",
            color_discrete_map={"Income": GREEN, "Expenses": RED},
            title="Income vs Expenses by Month",
        )
        fig_inc.update_xaxes(title="", type="category")
        fig_inc.update_yaxes(title="Amount ($)")
        st.plotly_chart(style_fig(fig_inc), use_container_width=True)

        section("Income Records")
        st.dataframe(
            df_income.sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "description": "Source",
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            },
        )

# ── Tab 5: Recurring Transactions ─────────────────────────────────────────────
with tab5:
    section("Recurring Transactions", "Merchants that appear consistently across multiple months")

    recurring_df = detect_recurring(df_filtered, min_months=2, tolerance=0.10)

    if recurring_df.empty:
        notice(
            "No recurring transactions detected. "
            "At least 2 months of data with consistent amounts are needed."
        )
    else:
        r1, r2 = st.columns(2)
        with r1:
            metric_card(
                "Recurring Merchants",
                str(len(recurring_df)),
                "Detected across multiple months",
                TEAL,
            )
        with r2:
            monthly_recurring_cost = recurring_df[
                recurring_df["frequency"] == "Monthly"
            ]["avg_amount"].sum()
            metric_card(
                "Est. Monthly Recurring Cost",
                f"${monthly_recurring_cost:,.2f}",
                "Sum of all monthly recurring merchants",
                CORAL,
            )

        st.write("")
        st.dataframe(
            recurring_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "description":  "Merchant",
                "avg_amount":   st.column_config.NumberColumn("Avg Amount",   format="$%.2f"),
                "occurrences":  st.column_config.NumberColumn("Occurrences",  format="%d"),
                "months_seen":  st.column_config.NumberColumn("Months Seen",  format="%d"),
                "frequency":    "Frequency",
            },
        )

st.markdown(
    '<div class="footer">SPENDSENSE &nbsp;|&nbsp; Built with Streamlit, Pandas and Plotly</div>',
    unsafe_allow_html=True,
)