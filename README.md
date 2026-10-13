# 💚 BudgetWise

### Personal Finance Dashboard | Python • Streamlit • SQLite • Plotly

BudgetWise is an interactive personal finance application built with Python. It helps users track monthly expenses, monitor available income, visualize spending habits, and evaluate savings goals through a modern dashboard.

## Features

- **Financial Dashboard:** View monthly income, expenses, available balance, and savings targets.
- **Expense Management:** Add, edit, delete, search, and filter transactions.
- **Monthly Analytics:** Analyze spending trends and category breakdowns with interactive Plotly charts.
- **Savings Goal Tracking:** Estimate how much of a savings goal could be covered by available monthly income.
- **Data Export:** Download filtered transactions as CSV files.
- **Local Database:** Store financial records using SQLite.
- **Automated Testing:** Validate financial calculations with Python's unittest framework.
- **Responsive Design:** Premium dark interface with emerald green, orange, and yellow accents.

## Technology Stack

| Technology   | Purpose                    |
| ------------ | -------------------------- |
| Python       | Application logic          |
| Streamlit    | Web interface              |
| SQLite       | Local data storage         |
| Pandas       | Data processing            |
| Plotly       | Interactive visualizations |
| unittest     | Automated financial tests  |
| Git & GitHub | Version control            |

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/deiondouglas00-web/BudgetWise.git
cd BudgetWise
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**4. Launch BudgetWise**

```bash
python -m streamlit run dashboard.py
```

The application will open in your browser.

## Running Automated Tests

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
BudgetWise/
├── dashboard.py
├── database.py
├── finance.py
├── requirements.txt
├── .gitignore
├── README.md
└── tests/
    └── test_finance.py
```

## Financial Calculation Logic

BudgetWise calculates:

- **Monthly Expenses:** Total valid expenses recorded for the selected month.
- **Available Balance:** Configured monthly income minus monthly expenses.
- **Savings Capacity:** Available balance, with negative values treated as zero.
- **Savings Goal Coverage:** Savings capacity divided by the configured savings goal.

Savings capacity is an estimate, not a record of actual savings deposits. Historical income uses the current monthly income setting.

## Roadmap

- [x] Build the Streamlit dashboard
- [x] Implement SQLite transaction management
- [x] Add interactive financial charts
- [x] Implement monthly reporting
- [x] Add savings goal tracking
- [x] Implement automated financial calculation tests
- [ ] Complete deployment and data privacy review
- [ ] Publish GitHub repository
- [ ] Deploy a safe online portfolio demo
- [ ] Add application screenshots

## Privacy

BudgetWise currently stores financial records locally in SQLite. Personal financial data and environment secrets should never be committed to a public repository.

The project is intended as a portfolio application and is not financial advice.

## Developer

**Deion Douglas**

Houston, Texas

Master's Degree in Management Information Systems

Focus: Python Development • Data Analytics • Business Intelligence • Application Development

