import sqlite3

from bot.constants import DB_PATH, TransactionType


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_transaction(user_id: int, amount: int, transaction_type: TransactionType, description: str = None):
    amount = abs(amount) if transaction_type == TransactionType.INCOME else -abs(amount)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (telegram_user_id, type, amount, description) VALUES (?, ?, ?, ?)",
        (user_id, transaction_type.value, f"{amount}", description)
    )

    conn.commit()
    conn.close()


def get_total() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) total FROM transactions")
    row = cursor.fetchone()

    conn.close()

    total = row["total"] or 0
    return int(total)
