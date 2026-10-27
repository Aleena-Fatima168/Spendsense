# SpendSense — Personal Finance Analyzer

A professional personal finance dashboard built with Python and Streamlit. Upload your transaction CSV, get automatic AI-powered categorization, smart insights, budget tracking, and a downloadable PDF report.

---

## Features

- **Smart Categorization** — Rule-based engine + Gemini AI for unknown merchants
- **Interactive Dashboard** — 5 tabs: Overview, Trends, Transactions, Income & Savings, Recurring
- **Budget Tracker** — Set a monthly budget and track progress with alerts
- **Income Tracking** — Upload income data and see your net savings rate
- **Recurring Detection** — Automatically detects subscriptions and regular bills
- **PDF Report Export** — Download a professional summary report
- **SQLite Persistence** — Data saves between sessions, no re-uploading needed
- **Spending Insights** — Auto-generated plain-English insights comparing months
- **Charts** — Donut chart, stacked bar, heatmap, weekday patterns, top merchants
- **Unit Tested** — 20 tests covering all core modules

---

## Project Structure

```
Finance_analyzer/
├── app.py                      # Main Streamlit dashboard
├── analyze.py                  # Monthly totals + insight generation
├── categorize.py               # Rule-based transaction categorizer
├── llm_categorize.py           # Gemini AI categorizer for unknown merchants
├── database.py                 # SQLite persistence layer
├── recurring.py                # Recurring transaction detection
├── report.py                   # PDF report generator
├── evaluate.py                 # Categorization accuracy evaluation
├── generate_data.py            # Sample data generator
├── tests.py                    # Unit tests (pytest)
├── transactions.csv            # Sample transaction data
├── transactions_categorized.csv# Categorized sample data
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── config.toml             # Streamlit theme config
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Finance_analyzer.git
cd Finance_analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate sample data (optional)

```bash
python generate_data.py
python categorize.py
```

### 5. Run the dashboard

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## AI Categorization (Optional)

To enable AI categorization for unknown merchants, set your Gemini API key:

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Mac/Linux
export GEMINI_API_KEY=your_api_key_here
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/).

---

## CSV Format

Your transaction CSV must have these columns:

| Column | Description | Example |
|---|---|---|
| `date` | Transaction date | `2026-06-15` |
| `description` | Merchant name | `Starbucks` |
| `amount` | Amount spent | `12.50` |

---

## Running Tests

```bash
pytest tests.py -v
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Dashboard UI |
| Pandas | Data processing |
| Plotly | Charts |
| SQLite | Data persistence |
| fpdf2 | PDF generation |
| Google Gemini | AI categorization |
| pytest | Unit testing |

---

## Screenshots

> Add screenshots of your dashboard here after deploying.

---

## License

MIT License — free to use and modify.
