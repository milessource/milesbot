from __future__ import annotations

import sqlite3
from uuid import uuid4

def _request_connection() -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection with a row factory for dictionary-like access.
    """
    connection = sqlite3.connect("._wallet_database_SQL__.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_database_if_not_exists() -> None:
    """
    Initializes the database by creating the required tables if they do not already exist.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 100000
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                uuid TEXT PRIMARY KEY,
                product_name TEXT,
                product_cost INTEGER,
                user_id INTEGER,
                status TEXT DEFAULT 'pending'
            )
        ''')
        connection.commit()


def create_account(user_id: int) -> None:
    """
    Creates an account for the specified user ID if it does not already exist.
    :param user_id: The ID of the user.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO accounts (user_id) VALUES (?)",
            (user_id,))
        connection.commit()


def request_balance(user_id: int) -> int | None:
    """
    Retrieves the balance for the specified user ID.
    :param user_id: The ID of the user.
    :return: The user's balance, or None if the account does not exist.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = ?",
            (user_id,))
        row = cursor.fetchone()
        return row["balance"] if row else None


def update_balance(user_id: int, amount: int) -> None:
    """
    Updates the balance for the specified user ID by adding the specified amount.
    :param user_id: The ID of the user.
    :param amount: The amount to add (or subtract, if negative).
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id))
        connection.commit()


def create_transaction(user_id: int, product_name: str, product_cost: int) -> str:
    """
    Creates a transaction for a product purchase.
    :param user_id: The ID of the user.
    :param product_name: The name of the product.
    :param product_cost: The cost of the product.
    :return: The UUID of the created transaction.
    """
    uuid: str = str(uuid4())
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO transactions (uuid, product_name, product_cost, user_id) VALUES (?, ?, ?, ?)",
            (uuid, product_name, product_cost, user_id))
        connection.commit()
    return uuid


def apply_transaction(uuid: str) -> bool:
    """
    Approves a transaction and deducts the cost from the user's balance if the transaction is pending.
    :param uuid: The UUID of the transaction.
    :return: True if the transaction was successfully applied, False otherwise.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT product_cost, user_id, status FROM transactions WHERE uuid = ?",
            (uuid,))
        transaction = cursor.fetchone()
        if transaction and transaction["status"] == "pending":
            user_id = transaction["user_id"]
            cost = transaction["product_cost"]
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
                (cost, user_id))
            cursor.execute(
                "UPDATE transactions SET status = 'approved' WHERE uuid = ?",
                (uuid,))
            connection.commit()
            return True
    return False


def request_transaction_status(uuid: str) -> str | None:
    """
    Retrieves the status of a transaction by its UUID.
    :param uuid: The UUID of the transaction.
    :return: The status of the transaction, or None if the transaction does not exist.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT status FROM transactions WHERE uuid = ?",
            (uuid,))
        row = cursor.fetchone()
        return row["status"] if row else None


def transfer_money(from_user: int, to_user: int, amount: int) -> bool:
    """
    Transfers money from one user to another if the sender has sufficient balance.
    :param from_user: The ID of the sender.
    :param to_user: The ID of the recipient.
    :param amount: The amount to transfer.
    :return: True if the transfer was successful, False otherwise.
    """
    with _request_connection() as connection:
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = ?",
            (from_user,))
        if cursor.fetchone()["balance"] >= amount:
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
                (amount, from_user))
            cursor.execute(
                "UPDATE accounts SET balance = balance + ? WHERE user_id = ?",
                (amount, to_user))
            connection.commit()
            return True
    return False
