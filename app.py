
"""BudgetWise public portfolio demo entry point."""

import os

# Always enable fictional, read-only data
# before importing the dashboard.
os.environ["BUDGETWISE_DEMO_MODE"] = "true"

import dashboard
