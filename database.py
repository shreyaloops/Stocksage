import sqlite3


def get_connection():
    return sqlite3.connect("portfolio.db")


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_holding(name, symbol, quantity, buy_price):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO holdings
        (name, symbol, quantity, buy_price)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        symbol,
        quantity,
        buy_price
    ))

    conn.commit()
    conn.close()


def get_holdings():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, symbol, quantity, buy_price
        FROM holdings
    """)

    holdings = cursor.fetchall()

    conn.close()

    return holdings


def delete_holding(holding_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM holdings WHERE id = ?",
        (holding_id,)
    )

    conn.commit()
    conn.close()


initialize_database()
