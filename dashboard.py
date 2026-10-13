

"""BudgetWise v1.0 — Personal Finance Dashboard."""

from datetime import date, datetime
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    DEMO_MODE,
    create_database,
    load_transactions,
    load_setting,
    save_setting,
    save_transaction,
    update_transaction,
    delete_transaction,
)

from finance import (
    budget_summary,
    monthly_series,
    nonnegative_money,
    positive_money,
)


# ==========================================
# CONFIGURATION
# ==========================================

BG = "#0F1117"
CARD = "#1C2028"
BORDER = "#303741"
GREEN = "#10B981"
ORANGE = "#F97316"
YELLOW = "#FACC15"
TEXT = "#F9FAFB"
MUTED = "#9CA3AF"

PALETTE = [
    ORANGE, GREEN, YELLOW, "#3B82F6",
    "#A78BFA", "#EC4899", "#14B8A6",
]

CATEGORIES = [
    "Housing",
    "Groceries",
    "Food",
    "Transportation",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Education",
    "Other",
]

st.set_page_config(
    page_title=(
        "BudgetWise Demo"
        if DEMO_MODE
        else "BudgetWise | Personal Finance"
    ),
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# CUSTOM STYLING
# ==========================================

st.markdown("""
<style>
:root {
    color-scheme: dark;
}

.stApp {
    background: #0F1117;
    color: #F9FAFB;
}

[data-testid="stSidebar"] {
    background: #151A21;
    border-right: 1px solid #303741;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #F9FAFB !important;
    letter-spacing: -0.5px;
}

.bw-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 3px;
}

.bw-brand-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: #12382E;
    color: #10B981;
    display: grid;
    place-items: center;
    font-size: 1.7rem;
}

.bw-brand-name {
    font-size: 1.4rem;
    font-weight: 800;
    color: #F9FAFB;
}

.bw-brand-subtitle {
    font-size: .65rem;
    color: #9CA3AF;
    letter-spacing: .17em;
}

.bw-card {
    background: #1C2028;
    border: 1px solid #303741;
    border-radius: 18px;
    padding: 21px;
    min-height: 165px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(0,0,0,.12);
    transition: transform .22s ease;
}

.bw-card:hover {
    transform: translateY(-4px);
}

.bw-card-label {
    font-size: .92rem;
    font-weight: 600;
    color: #C5CAD2;
}

.bw-card-value {
    color: #F9FAFB;
    font-size: clamp(1.3rem,2.2vw,2rem);
    font-weight: 800;
    margin-top: 12px;
}

.bw-card-note {
    color: #9CA3AF;
    font-size: .77rem;
    margin-top: 7px;
}

.bw-card-line {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--accent);
}

.bw-progress-track {
    background: #303741;
    height: 14px;
    border-radius: 20px;
    overflow: hidden;
}

.bw-progress-fill {
    height: 100%;
    background: linear-gradient(
        90deg, #FACC15, #F97316
    );
    border-radius: 20px;
}

[data-testid="stForm"] {
    background: #1C2028;
    border: 1px solid #303741;
    border-radius: 16px;
    padding: 15px;
}

@media(max-width:768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .bw-card {
        min-height: 135px;
        padding: 16px;
    }
}

@media(prefers-reduced-motion:reduce) {
    .bw-card {
        transition: none;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# HELPERS
# ==========================================

def html(markup):
    compact = "".join(
        line.strip()
        for line in markup.splitlines()
    )
    st.markdown(
        compact,
        unsafe_allow_html=True
    )


def cash(value):
    amount = float(value)

    if amount < 0:
        return f"-${abs(amount):,.2f}"

    return f"${amount:,.2f}"


def card(label, amount, accent, icon, note):
    if accent not in (GREEN, ORANGE, YELLOW):
        accent = GREEN

    html(f"""
    <div class="bw-card" style="--accent:{accent}">
        <div class="bw-card-label">
            {escape(icon)} {escape(label)}
        </div>
        <div class="bw-card-value">
            {escape(cash(amount))}
        </div>
        <div class="bw-card-note">
            {escape(note)}
        </div>
        <div class="bw-card-line"></div>
    </div>
    """)


def chart_theme(fig, height=365):
    fig.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font_color=TEXT,
        height=height,
        margin=dict(l=20, r=20, t=60, b=30),
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0.5,
            xanchor="center",
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
    )

    fig.update_yaxes(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
    )

    return fig


def transaction_frame(records):
    columns = [
        "id",
        "transaction_date",
        "category",
        "description",
        "amount",
    ]

    df = pd.DataFrame(records)

    for column in columns:
        if column not in df:
            df[column] = pd.Series(dtype="object")

    df = df[columns].copy()

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce",
    )

    df["month"] = (
        df["transaction_date"]
        .dt.strftime("%Y-%m")
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    ).fillna(0)

    return df


def transaction_table(df, include_id=False):
    columns = [
        "transaction_date",
        "category",
        "description",
        "amount",
    ]

    if include_id:
        columns.insert(0, "id")

    display = df[columns].copy()

    display["transaction_date"] = (
        display["transaction_date"]
        .dt.strftime("%b %d, %Y")
        .fillna("Undated")
    )

    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "transaction_date": "Date",
            "category": "Category",
            "description": "Description",
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="$%.2f",
            ),
            "id": "ID",
        },
    )


def date_months(df):
    current = date.today().strftime("%Y-%m")

    return sorted(
        set(df["month"].dropna().tolist())
        | {current},
        reverse=True,
    )


def save_expense(category, description, amount, when):
    if DEMO_MODE:
        raise PermissionError(
            "Changes are disabled in demo mode."
        )

    if not description.strip():
        raise ValueError(
            "Description is required."
        )

    if not category.strip():
        raise ValueError(
            "Category is required."
        )

    if len(description.strip()) > 200:
        raise ValueError(
            "Description must be 200 characters or fewer."
        )

    value = positive_money(amount)

    save_transaction(
        category.strip(),
        description.strip(),
        float(value),
        when.isoformat(),
    )


# ==========================================
# LOAD FINANCIAL DATA
# ==========================================

try:
    create_database()

    transactions = load_transactions()

    monthly_income = nonnegative_money(
        load_setting("monthly_income") or 0
    )

    savings_goal = nonnegative_money(
        load_setting("savings_goal") or 0
    )

except Exception as exc:
    st.error(
        "BudgetWise could not load its data."
    )
    st.exception(exc)
    st.stop()


frame = transaction_frame(transactions)
months = date_months(frame)


# ==========================================
# DEMO NOTICE
# ==========================================

if DEMO_MODE:
    st.info(
        "PUBLIC DEMO — All financial information "
        "shown is fictional. This portfolio "
        "demonstration is read-only. No financial "
        "information is collected or saved."
    )


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    html("""
    <div class="bw-brand">
        <div class="bw-brand-icon">◈</div>
        <div>
            <div class="bw-brand-name">
                BudgetWise
            </div>
            <div class="bw-brand-subtitle">
                PERSONAL FINANCE
            </div>
        </div>
    </div>
    """)

    st.divider()

    if DEMO_MODE:
        pages = [
            "Dashboard",
            "Monthly Analytics",
            "Manage Transactions",
        ]
    else:
        pages = [
            "Dashboard",
            "Monthly Analytics",
            "Add Expense",
            "Manage Transactions",
            "Settings",
        ]

    page = st.radio(
        "Navigation",
        pages,
        label_visibility="collapsed",
    )

    st.divider()

    if DEMO_MODE:
        st.caption("BUDGETWISE v1.0 · PUBLIC DEMO")
    else:
        st.caption("BUDGETWISE v1.0")

    st.caption(
        "Your money. Your goals. Your future."
    )


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.caption("DASHBOARD")
    st.title("Financial Overview")

    st.caption(
        "Track your income, expenses, and "
        "savings capacity in one place."
    )

    selected = st.selectbox(
        "Reporting Month",
        months,
        format_func=lambda month: (
            datetime.strptime(
                month,
                "%Y-%m",
            ).strftime("%B %Y")
        ),
    )

    summary = budget_summary(
        transactions,
        selected,
        monthly_income,
        savings_goal,
    )

    current = frame[
        frame["month"] == selected
    ].copy()

    a, b, c, d = st.columns(4)

    with a:
        card(
            "Monthly Income",
            summary["income"],
            GREEN,
            "↗",
            "Configured monthly income",
        )

    with b:
        card(
            "Monthly Expenses",
            summary["expenses"],
            ORANGE,
            "↘",
            f"{summary['count']} dated transactions",
        )

    with c:
        card(
            "Available Balance",
            summary["balance"],
            GREEN if summary["balance"] >= 0 else ORANGE,
            "◉",
            "Income minus monthly expenses",
        )

    with d:
        card(
            "Savings Goal",
            summary["goal"],
            YELLOW,
            "◎",
            "Target, not actual savings",
        )

    st.write("")

    if summary["spending_pct"] is None:
        st.info(
            "Set monthly income in Settings "
            "to calculate spending percentage."
        )

    elif summary["balance"] < 0:
        st.error(
            "Expenses exceed monthly income by "
            f"{cash(abs(summary['balance']))}."
        )

    else:
        st.caption(
            "You have spent "
            f"{summary['spending_pct']:.1f}% "
            "of your configured monthly income."
        )

    st.subheader("🎯 Savings Goal Coverage")

    if summary["goal"] > 0:

        pct = min(
            max(
                float(summary["goal_coverage_pct"]),
                0,
            ),
            100,
        )

        html(f"""
        <div class="bw-progress-track">
            <div
                class="bw-progress-fill"
                style="width:{pct:.1f}%">
            </div>
        </div>
        """)

        st.caption(
            "Available budget could cover "
            f"{float(summary['goal_coverage_pct']):.1f}% "
            "of your savings goal. "
            "This is not money already saved."
        )

        if summary["goal_shortfall"] > 0:
            st.warning(
                "You need "
                f"{cash(summary['goal_shortfall'])} "
                "more budget capacity to cover your goal."
            )
        else:
            st.success(
                "Your available budget can cover "
                "your goal, leaving "
                f"{cash(summary['after_goal'])} afterward."
            )

    else:
        st.info(
            "Set a savings goal in Settings "
            "to see goal coverage."
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Income vs Expenses")

        anchor = date.fromisoformat(
            f"{selected}-01"
        )

        series_months = []

        for offset in range(5, -1, -1):
            index = (
                anchor.year * 12
                + anchor.month
                - 1
                - offset
            )

            series_months.append(
                f"{index // 12:04d}-{index % 12 + 1:02d}"
            )

        trend = pd.DataFrame(
            monthly_series(
                transactions,
                series_months,
            )
        )

        trend["income"] = float(monthly_income)

        melted = trend.melt(
            id_vars="month",
            value_vars=["income", "expenses"],
            var_name="Type",
            value_name="Amount",
        )

        fig = px.bar(
            melted,
            x="month",
            y="Amount",
            color="Type",
            barmode="group",
            title="Last 6 Months (Configured Income)",
            color_discrete_map={
                "income": GREEN,
                "expenses": ORANGE,
            },
            labels={
                "month": "",
                "Amount": "Amount ($)",
            },
        )

        st.plotly_chart(
            chart_theme(fig),
            use_container_width=True,
        )

    with right:
        st.subheader("Spending by Category")

        category_values = summary["categories"]

        if category_values:

            fig = px.pie(
                names=list(category_values),
                values=[
                    float(value)
                    for value in category_values.values()
                ],
                hole=0.62,
                title=f"{selected} Expenses",
                color_discrete_sequence=PALETTE,
            )

            fig.update_traces(
                textinfo="percent",
                hovertemplate=(
                    "%{label}: $%{value:,.2f}"
                    "<extra></extra>"
                ),
            )

            st.plotly_chart(
                chart_theme(fig),
                use_container_width=True,
            )

        else:
            st.info(
                "No dated expenses for this month."
            )

    st.subheader("Recent Transactions")

    if not current.empty:
        transaction_table(
            current.sort_values(
                ["transaction_date", "id"],
                ascending=False,
            ).head(10)
        )
    else:
        st.info(
            "No transactions recorded for this month."
        )

    undated = int(
        frame["transaction_date"].isna().sum()
    )

    if undated:
        st.warning(
            f"{undated} transaction(s) have no valid date "
            "and are excluded from monthly analytics."
        )

    st.caption(
        "Historical income uses the current income "
        "setting; separate monthly income history "
        "is not stored."
    )


# ==========================================
# MONTHLY ANALYTICS
# ==========================================

elif page == "Monthly Analytics":

    st.title("Monthly Analytics")

    st.caption(
        "Explore expenses across reporting months."
    )

    selected = st.selectbox(
        "Reporting Month",
        months,
        format_func=lambda month: (
            datetime.strptime(
                month,
                "%Y-%m",
            ).strftime("%B %Y")
        ),
    )

    summary = budget_summary(
        transactions,
        selected,
        monthly_income,
        savings_goal,
    )

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Expenses",
            cash(summary["expenses"]),
        )

    with b:
        st.metric(
            "Transactions",
            summary["count"],
        )

    with c:
        st.metric(
            "Balance",
            cash(summary["balance"]),
        )

    current = frame[
        frame["month"] == selected
    ].copy()

    if current.empty:
        st.info(
            "No dated expenses recorded for this month."
        )

    else:
        by_category = pd.DataFrame([
            {
                "Category": category,
                "Amount": float(amount),
            }
            for category, amount
            in summary["categories"].items()
        ]).sort_values(
            "Amount",
            ascending=False,
        )

        fig = px.bar(
            by_category,
            x="Category",
            y="Amount",
            color="Category",
            title="Category Breakdown",
            color_discrete_sequence=PALETTE,
        )

        fig.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            chart_theme(fig),
            use_container_width=True,
        )

        st.subheader(
            "Transactions for Selected Month"
        )

        transaction_table(
            current.sort_values(
                "transaction_date",
                ascending=False,
            )
        )


# ==========================================
# ADD EXPENSE — LOCAL MODE ONLY
# ==========================================

elif page == "Add Expense" and not DEMO_MODE:

    st.title("Add Expense")

    st.caption(
        "Record a dated expense so it appears "
        "in the correct reporting month."
    )

    with st.form(
        "add_expense_form",
        clear_on_submit=True,
    ):

        category = st.selectbox(
            "Expense Category",
            CATEGORIES,
        )

        description = st.text_input(
            "Description",
            max_chars=200,
            placeholder="e.g., Weekly groceries",
        )

        amount = st.number_input(
            "Amount ($)",
            min_value=0.01,
            value=0.01,
            step=1.00,
            format="%.2f",
        )

        when = st.date_input(
            "Transaction Date",
            value=date.today(),
        )

        submitted = st.form_submit_button(
            "Save Expense",
            type="primary",
        )

    if submitted:
        try:
            save_expense(
                category,
                description,
                amount,
                when,
            )

        except Exception as exc:
            st.error(
                f"Unable to save transaction: {exc}"
            )

        else:
            st.success(
                "Expense saved successfully!"
            )
            st.rerun()


# ==========================================
# MANAGE TRANSACTIONS
# ==========================================

elif page == "Manage Transactions":

    st.title("Manage Transactions")

    if DEMO_MODE:
        st.caption(
            "Filter and review fictional expenses. "
            "Editing and deletion are disabled."
        )
    else:
        st.caption(
            "Filter, review, edit, and delete "
            "recorded expenses."
        )

    if frame.empty:
        st.info(
            "No transactions available."
        )

    else:
        a, b, c = st.columns(3)

        with a:
            categories = sorted(
                frame["category"]
                .fillna("Other")
                .unique()
                .tolist()
            )

            cat = st.selectbox(
                "Category",
                ["All Categories"] + categories,
            )

        with b:
            month_options = [
                "All Months"
            ] + months

            if frame["month"].isna().any():
                month_options.append("Undated")

            month_filter = st.selectbox(
                "Month",
                month_options,
            )

        with c:
            search = st.text_input(
                "Search Description",
                placeholder="Search...",
            )

        filtered = frame.copy()

        if cat != "All Categories":
            filtered = filtered[
                filtered["category"] == cat
            ]

        if month_filter == "Undated":
            filtered = filtered[
                filtered["month"].isna()
            ]

        elif month_filter != "All Months":
            filtered = filtered[
                filtered["month"] == month_filter
            ]

        if search.strip():
            filtered = filtered[
                filtered["description"]
                .fillna("")
                .str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                )
            ]

        st.caption(
            f"{len(filtered)} transaction(s) found"
        )

        transaction_table(
            filtered.sort_values(
                ["transaction_date", "id"],
                ascending=False,
            ),
            include_id=True,
        )

        if not filtered.empty:

            csv = filtered[
                [
                    "id",
                    "transaction_date",
                    "category",
                    "description",
                    "amount",
                ]
            ].to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Filtered CSV",
                csv,
                file_name="budgetwise_transactions.csv",
                mime="text/csv",
            )

        # Demo mode ends here.
        # No editing controls are displayed.
        if DEMO_MODE:
            st.info(
                "Read-only demo: transactions cannot "
                "be added, edited, or deleted."
            )

        else:
            st.divider()

            options = {
                (
                    f"#{transaction['id']} · "
                    f"{transaction['description']} · "
                    f"{cash(transaction['amount'])}"
                ): transaction
                for transaction in transactions
            }

            label = st.selectbox(
                "Choose a Transaction to Manage",
                list(options),
            )

            selected = options[label]

            edit_tab, delete_tab = st.tabs([
                "✏️ Edit",
                "🗑️ Delete",
            ])

            with edit_tab:

                st.caption(
                    "Edit category, description, and amount. "
                    "Existing dates are preserved."
                )

                with st.form(
                    f"edit_{selected['id']}"
                ):

                    current_category = str(
                        selected.get("category") or "Other"
                    )

                    category_options = list(
                        dict.fromkeys(
                            CATEGORIES + [current_category]
                        )
                    )

                    new_category = st.selectbox(
                        "Category",
                        category_options,
                        index=category_options.index(
                            current_category
                        ),
                    )

                    new_description = st.text_input(
                        "Description",
                        value=str(
                            selected.get("description") or ""
                        ),
                        max_chars=200,
                    )

                    new_amount = st.number_input(
                        "Amount ($)",
                        min_value=0.01,
                        value=max(
                            float(
                                selected.get("amount") or 0
                            ),
                            0.01,
                        ),
                        step=1.00,
                        format="%.2f",
                    )

                    update_clicked = (
                        st.form_submit_button(
                            "Update Transaction",
                            type="primary",
                        )
                    )

                if update_clicked:
                    try:
                        if not new_description.strip():
                            raise ValueError(
                                "Description is required."
                            )

                        value = positive_money(
                            new_amount
                        )

                        updated = update_transaction(
                            selected["id"],
                            new_category,
                            new_description.strip(),
                            float(value),
                        )

                        if updated:
                            st.success(
                                "Transaction updated."
                            )
                            st.rerun()
                        else:
                            st.error(
                                "Transaction not found."
                            )

                    except Exception as exc:
                        st.error(
                            f"Unable to update: {exc}"
                        )

            with delete_tab:

                st.warning(
                    "Deletion is permanent. "
                    "Verify the selected transaction."
                )

                confirm = st.checkbox(
                    "I want to permanently delete "
                    f"transaction #{selected['id']}",
                    key=f"confirm_{selected['id']}",
                )

                if st.button(
                    "Delete Transaction",
                    disabled=not confirm,
                    type="primary",
                ):
                    try:
                        deleted = delete_transaction(
                            selected["id"]
                        )

                        if deleted:
                            st.success(
                                "Transaction deleted."
                            )
                            st.rerun()
                        else:
                            st.error(
                                "Transaction not found."
                            )

                    except Exception as exc:
                        st.error(
                            f"Unable to delete: {exc}"
                        )


# ==========================================
# SETTINGS — LOCAL MODE ONLY
# ==========================================

elif page == "Settings" and not DEMO_MODE:

    st.title("Budget Settings")

    st.caption(
        "These settings apply to every reporting month. "
        "Historical monthly settings are not stored."
    )

    with st.form(
        "budget_settings_form"
    ):

        income_input = st.number_input(
            "Monthly Income ($)",
            min_value=0.0,
            value=float(monthly_income),
            step=100.0,
            format="%.2f",
        )

        goal_input = st.number_input(
            "Monthly Savings Goal ($)",
            min_value=0.0,
            value=float(savings_goal),
            step=50.0,
            format="%.2f",
        )

        clicked = st.form_submit_button(
            "Save Settings",
            type="primary",
        )

    if clicked:
        try:
            income_value = nonnegative_money(
                income_input
            )

            goal_value = nonnegative_money(
                goal_input
            )

            save_setting(
                "monthly_income",
                float(income_value),
            )

            save_setting(
                "savings_goal",
                float(goal_value),
            )

        except Exception as exc:
            st.error(
                f"Could not save settings: {exc}"
            )

        else:
            st.success(
                "Settings saved!"
            )
            st.rerun()

    st.divider()

    st.subheader(
        "Current Configuration"
    )

    a, b = st.columns(2)

    with a:
        st.metric(
            "Monthly Income",
            cash(monthly_income),
        )

    with b:
        st.metric(
            "Savings Goal",
            cash(savings_goal),
        )

    st.info(
        "Savings goal coverage estimates how much "
        "of your budget could be saved. "
        "It does not track actual savings deposits."
    )

    st.warning(
        "Keep a backup of your SQLite database "
        "before replacing or moving application files."
    )


