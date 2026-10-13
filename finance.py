
"""BudgetWise v0.9 — Financial calculation engine."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a monetary value")

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Invalid monetary amount") from exc

    if not amount.is_finite():
        raise ValueError("Amount must be finite")

    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def positive_money(value):
    amount = money(value)
    if amount <= 0:
        raise ValueError("Transaction amount must be greater than zero")
    return amount


def nonnegative_money(value):
    amount = money(value)
    if amount < 0:
        raise ValueError("Setting must not be negative")
    return amount


def month_key(value):
    if value is None or value == "":
        return None

    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m")

    try:
        return date.fromisoformat(str(value)[:10]).strftime("%Y-%m")
    except (TypeError, ValueError):
        return None


def month_totals(transactions, month):
    total = Decimal("0.00")
    categories = {}
    count = 0

    for transaction in transactions:
        if month_key(transaction.get("transaction_date")) != month:
            continue

        amount = money(transaction.get("amount", 0))

        if amount < 0:
            continue

        category = str(
            transaction.get("category") or "Other"
        ).strip() or "Other"

        total += amount
        categories[category] = (
            categories.get(category, Decimal("0.00")) + amount
        )
        count += 1

    return {
        "expenses": total,
        "categories": categories,
        "count": count,
    }


def budget_summary(transactions, month, income, goal):
    income = nonnegative_money(income)
    goal = nonnegative_money(goal)

    monthly = month_totals(transactions, month)
    expenses = monthly["expenses"]
    balance = income - expenses
    capacity = max(balance, Decimal("0.00"))

    coverage = (
        capacity / goal * 100
        if goal > 0
        else Decimal("0")
    )

    spend_pct = (
        expenses / income * 100
        if income > 0
        else None
    )

    return {
        **monthly,
        "income": income,
        "goal": goal,
        "balance": balance,
        "savings_capacity": capacity,
        "goal_coverage_pct": coverage,
        "spending_pct": spend_pct,
        "goal_shortfall": max(
            goal - capacity, Decimal("0.00")
        ),
        "after_goal": balance - goal,
    }


def monthly_series(transactions, months):
    return [
        {
            "month": month,
            "expenses": float(
                month_totals(transactions, month)["expenses"]
            ),
        }
        for month in months
    ]
