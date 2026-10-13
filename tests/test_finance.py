
import unittest
from decimal import Decimal

from finance import (
    money,
    positive_money,
    nonnegative_money,
    month_key,
    month_totals,
    budget_summary,
    monthly_series,
)


class TestBudgetWiseFinance(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            {
                "category": "Food",
                "amount": 100,
                "transaction_date": "2026-10-01",
            },
            {
                "category": "Transportation",
                "amount": 50,
                "transaction_date": "2026-10-10",
            },
            {
                "category": "Food",
                "amount": 25,
                "transaction_date": "2026-09-20",
            },
            {
                "category": "Other",
                "amount": 80,
                "transaction_date": None,
            },
        ]

    def test_currency_rounding(self):
        self.assertEqual(
            money("19.995"),
            Decimal("20.00"),
        )

    def test_reject_invalid_money(self):
        for value in ["nan", "inf", None, True, "abc"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    money(value)

    def test_reject_zero_expense(self):
        with self.assertRaises(ValueError):
            positive_money(0)

    def test_reject_negative_setting(self):
        with self.assertRaises(ValueError):
            nonnegative_money(-100)

    def test_month_date(self):
        self.assertEqual(
            month_key("2026-10-15"),
            "2026-10",
        )

    def test_invalid_date(self):
        self.assertIsNone(month_key("invalid"))

    def test_monthly_expenses(self):
        result = month_totals(
            self.transactions, "2026-10"
        )
        self.assertEqual(
            result["expenses"],
            Decimal("150.00"),
        )

    def test_transaction_count(self):
        result = month_totals(
            self.transactions, "2026-10"
        )
        self.assertEqual(result["count"], 2)

    def test_category_totals(self):
        result = month_totals(
            self.transactions, "2026-10"
        )
        self.assertEqual(
            result["categories"]["Food"],
            Decimal("100.00"),
        )

    def test_available_balance(self):
        result = budget_summary(
            self.transactions, "2026-10", 5000, 1000
        )
        self.assertEqual(
            result["balance"],
            Decimal("4850.00"),
        )

    def test_savings_capacity(self):
        result = budget_summary(
            self.transactions, "2026-10", 5000, 1000
        )
        self.assertEqual(
            result["savings_capacity"],
            Decimal("4850.00"),
        )

    def test_overspending(self):
        result = budget_summary(
            self.transactions, "2026-10", 100, 1000
        )
        self.assertEqual(
            result["balance"],
            Decimal("-50.00"),
        )
        self.assertEqual(
            result["savings_capacity"],
            Decimal("0.00"),
        )

    def test_goal_shortfall(self):
        result = budget_summary(
            self.transactions, "2026-10", 500, 400
        )
        self.assertEqual(
            result["goal_shortfall"],
            Decimal("50.00"),
        )

    def test_zero_income(self):
        result = budget_summary(
            [], "2026-10", 0, 0
        )
        self.assertIsNone(result["spending_pct"])

    def test_monthly_series(self):
        result = monthly_series(
            self.transactions,
            ["2026-09", "2026-10"],
        )
        self.assertEqual(
            result[0]["expenses"], 25.0
        )
        self.assertEqual(
            result[1]["expenses"], 150.0
        )


if __name__ == "__main__":
    unittest.main()
