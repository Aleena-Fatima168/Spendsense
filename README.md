# SpendSense — Personal Finance Analyzer

> Track your spending. Understand your habits. Take control of your money.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://spendsen-7pbvrc4edkfsyrxxcgdtxw.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Spendsense-181717?style=for-the-badge&logo=github)](https://github.com/Aleena-Fatima168/Spendsense)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-20%20Passing-4CAF50?style=for-the-badge)](tests.py)

---

## Overview

**SpendSense** is a full-featured personal finance dashboard that turns raw transaction data into clear, actionable insights. Simply upload a CSV of your bank transactions and SpendSense will automatically categorize every purchase, visualize your spending patterns, detect recurring bills, track your budget, and generate a downloadable PDF report — all in seconds.

Built with Python and Streamlit, it combines a rule-based categorization engine with Google Gemini AI to handle even unknown merchants with high accuracy.

**Live at:** [https://spendsen-7pbvrc4edkfsyrxxcgdtxw.streamlit.app](https://spendsen-7pbvrc4edkfsyrxxcgdtxw.streamlit.app)

---

## Features

### Smart Categorization
Transactions are categorized using a fast rule-based engine. Any merchant not matched by a rule is sent to Google Gemini AI for intelligent classification — giving you the best of both speed and accuracy.

### Interactive 5-Tab Dashboard
| Tab | What it shows |
|---|---|
| Overview | KPI cards, insights, category breakdown, top merchants |
| Trends | Monthly bar chart, spending over time, weekday patterns, heatmap |
| Transactions | Searchable, sortable table with CSV and PDF export |
| Income & Savings | Income vs expenses comparison, net savings rate |
| Recurring | Auto-detected subscriptions and regular bills |

### Budget Tracker
Set a monthly budget from the sidebar. SpendSense shows a live progress bar and alerts you when you are approaching or over your limit.

### Income & Savings Rate
Upload a separate income CSV to see your total income, total expenses, net savings, and savings rate percentage — all in one view.

### Recurring Transaction Detection
SpendSense automatically identifies merchants that appear consistently across multiple months, helping you spot subscriptions and regular bills you may have forgotten about.

### PDF Report Export
Download a professionally formatted PDF report containing your KPI summary, category breakdown with progress bars, auto-generated insights, and your top 15 transactions.

### SQLite Persistence
Uploaded data is saved to a local SQLite database so you do not need to re-upload your CSV every time you open the app.

### Auto-Generated Insights
SpendSense compares your two most recent complete months and generates plain-English insights — telling you exactly where your spending went up or down and by how much.

---

## Project Structure

```
Spendsense/
├── app.py                        # Main Streamlit dashboard (5 tabs)
├── analyze.py                    # Monthly totals + insight generation
├── categorize.py                 # Rule-based transaction categorizer
├── llm_categorize.py             # Gemini AI categorizer for unknown merchants
├── database.py                   # SQLite persistence layer
├── recurring.py                  # Recurring transaction detection
├── report.py                     # PDF report generator
├── evaluate.py                   # Categorization accuracy evaluation
├── generate_data.py              # Sample data generator
├── tests.py                      # 20 unit tests (pytest)
├── transactions.csv              # Sample transaction data
├── transactions_categorized.csv  # Categorized sample data
├── requirements.txt              # Python dependencies
└── .streamlit/
    └── config.toml               # Streamlit theme configuration
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Aleena-Fatima168/Spendsense.git
cd Spendsense

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate sample data (optional)
python generate_data.py
python categorize.py

# 5. Run the dashboard
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## CSV Format

SpendSense accepts any CSV file with the following three columns:

| Column | Type | Description | Example |
|---|---|---|---|
| `date` | Date | Transaction date | `2026-06-15` |
| `description` | Text | Merchant or payee name | `Starbucks` |
| `amount` | Number | Amount spent (positive) | `12.50` |

> If your bank exports negative amounts for expenses, check the **"My CSV lists expenses as negative amounts"** option in the sidebar.

---

## AI Categorization

To enable Gemini AI categorization for unknown merchants, set your API key as an environment variable before starting the app:

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Mac / Linux
export GEMINI_API_KEY=your_api_key_here
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/).

---

## Running Tests

```bash
pytest tests.py -v
```

The test suite covers 20 cases across four modules:

| Module | Tests |
|---|---|
| `categorize.py` | Rule matching, case insensitivity, unknown merchants |
| `analyze.py` | Monthly totals, column validation, no negative totals |
| `analyze.py` | Insight generation, single-month edge case |
| `recurring.py` | Detection logic, empty input, single-occurrence exclusion |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Dashboard UI and deployment |
| Pandas | Data processing and aggregation |
| Plotly | Interactive charts and visualizations |
| SQLite | Local data persistence |
| fpdf2 | PDF report generation |
| Google Gemini | AI-powered merchant categorization |
| pytest | Unit testing |

---

## Author

**Aleena Fatima**
GitHub: [@Aleena-Fatima168](https://github.com/Aleena-Fatima168)

---

## License

MIT License — free to use, modify, and distribute.
