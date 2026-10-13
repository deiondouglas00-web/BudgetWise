from datetime import date
import sqlite3


# Create BudgetWise Database
def create_database():
    connection = sqlite3.connect("budgetwise.db")
    cursor = connection.cursor()

    # Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    # Add a transaction date column to older databases
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]

    if "transaction_date" not in columns:
        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN transaction_date TEXT
        """)

    # Application Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("BudgetWise database initialized successfully!")


# Save New Transaction

def save_transaction(category, description, amount, transaction_date=None):
    if transaction_date is None:
        transaction_date = date.today().isoformat()

    connection = sqlite3.connect("budgetwise.db")
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

    print("Transaction saved to database!")



# Load Saved Transactions

def load_transactions():
    connection = sqlite3.connect("budgetwise.db")
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
        transaction = {
            "id": row[0],
            "category": row[1],
            "description": row[2],
            "amount": row[3],
            "transaction_date": row[4]
        }

        transactions.append(transaction)

    return transactions



# Update Existing Transaction
def update_transaction(transaction_id, category, description, amount):
    connection = sqlite3.connect("budgetwise.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET category = ?, description = ?, amount = ?
        WHERE id = ?
    """, (category, description, amount, transaction_id))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows > 0


# Delete Existing Transaction
def delete_transaction(transaction_id):
    connection = sqlite3.connect("budgetwise.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    deleted_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted_rows > 0


# Save Income or Savings Goal
def save_setting(key, value):
    connection = sqlite3.connect("budgetwise.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (key, value))

    connection.commit()
    connection.close()


# Load Income or Savings Goal
def load_setting(key):
    connection = sqlite3.connect("budgetwise.db")
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


# Initialize Database
if __name__ == "__main__":
    create_database()


