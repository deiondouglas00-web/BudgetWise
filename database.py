
from datetime import date, timedelta
import os
import sqlite3


# ==========================================
# BUDGETWISE DATABASE CONFIGURATION
# ==========================================

DEMO_MODE = os.getenv(
    "BUDGETWISE_DEMO_MODE", "false"
).lower() in ("true", "1", "yes")

DATABASE_NAME = "budgetwise.db"


# ==========================================
# DEMO DATA
# ==========================================

def demo_transactions():
    today = date.today()
    month_start = today.replace(day=1)

    def demo_date(day):
        return (
            month_start + timedelta(days=day - 1)
        ).isoformat()

    sample_data = [
        ("Housing", "Monthly Rent", 1450.00, 1),
        ("Groceries", "Weekly Groceries", 125.75, 3),
        ("Transportation", "Gas", 65.00, 5),
        ("Entertainment", "Movie Night", 42.50, 7),
        ("Utilities", "Electricity", 135.25, 9),
        ("Food", "Lunch", 18.75, 10),
    ]

    return [
        {
            "id": index,
            "category": category,
            "description": description,
            "amount": amount,
            "transaction_date": demo_date(day)
        }
        for index, (
            category, description, amount, day
        ) in enumerate(sample_data, start=1)
    ]


DEMO_SETTINGS = {
    "monthly_income": 5200.00,
    "savings_goal": 1000.00,
}


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def require_local_mode():
    if DEMO_MODE:
        raise PermissionError(
            "BudgetWise is running in read-only "
            "demo mode. Changes are disabled."
        )


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def create_database():
    if DEMO_MODE:
        print("BudgetWise demo mode initialized.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [
        row[1] for row in cursor.fetchall()
    ]

    if "transaction_date" not in columns:
        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN transaction_date TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("BudgetWise database initialized!")


# ==========================================
# SAVE TRANSACTION
# ==========================================

def save_transaction(
    category,
    description,
    amount,
    transaction_date=None
):
    require_local_mode()

    if transaction_date is None:
        transaction_date = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            category,
            description,
            amount,
            transaction_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        category,
        description,
        amount,
        transaction_date
    ))

    connection.commit()
    connection.close()


# ==========================================
# LOAD TRANSACTIONS
# ==========================================

def load_transactions():
    if DEMO_MODE:
        return demo_transactions()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            category,
            description,
            amount,
            transaction_date
        FROM transactions
        ORDER BY id
    """)

    rows = cursor.fetchall()
    connection.close()

    transactions = []

    for row in rows:
        transactions.append({
            "id": row[0],
            "category": row[1],
            "description": row[2],
            "amount": row[3],
            "transaction_date": row[4]
        })

    return transactions


# ==========================================
# UPDATE TRANSACTION
# ==========================================

def update_transaction(
    transaction_id,
    category,
    description,
    amount
):
    require_local_mode()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET category = ?,
            description = ?,
            amount = ?
        WHERE id = ?
    """, (
        category,
        description,
        amount,
        transaction_id
    ))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows > 0


# ==========================================
# DELETE TRANSACTION
# ==========================================

def delete_transaction(transaction_id):
    require_local_mode()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    deleted_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted_rows > 0


# ==========================================
# SAVE SETTINGS
# ==========================================

def save_setting(key, value):
    require_local_mode()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (key, value))

    connection.commit()
    connection.close()


# ==========================================
# LOAD SETTINGS
# ==========================================

def load_setting(key):
    if DEMO_MODE:
        return DEMO_SETTINGS.get(key, 0.0)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT value FROM settings
        WHERE key = ?
    """, (key,))

    result = cursor.fetchone()
    connection.close()

    if result is not None:
        return result[0]

    return 0.0


# ==========================================
# INITIALIZE
# ==========================================

if __name__ == "__main__":
    create_database()



