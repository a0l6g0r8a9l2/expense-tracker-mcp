"""Data access layer for expense records."""

from __future__ import annotations

from typing import Optional

from app.database.db import DatabaseManager
from app.exceptions import DatabaseError
from app.logger import get_logger
from app.models.expense import Expense

logger = get_logger(__name__)


class ExpenseRepository:
    """Repository for expense data access operations."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize expense repository.
        
        Args:
            db_manager: Database manager instance
        """
        self._db = db_manager

    def add(self, expense: Expense) -> int:
        """Insert a new expense record.
        
        Args:
            expense: Expense object to insert
            
        Returns:
            ID of the inserted expense
            
        Raises:
            DatabaseError: If insert fails
        """
        try:
            expense_id = self._db.execute_insert(
                """
                INSERT INTO expenses(date, amount, category, subcategory, note, 
                                    original_currency, usd_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    expense.date,
                    expense.amount,
                    expense.category,
                    expense.subcategory,
                    expense.note,
                    expense.original_currency,
                    expense.usd_amount,
                ),
            )
            logger.info(f"Added expense {expense_id}: {expense.amount} {expense.original_currency}")
            return expense_id
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to add expense: {e}") from e

    def list(self, start_date: str, end_date: str) -> list[Expense]:
        """Get all expenses within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of Expense objects
            
        Raises:
            DatabaseError: If query fails
        """
        try:
            rows = self._db.execute_query(
                """
                SELECT id, date, amount, category, subcategory, note, 
                       original_currency, usd_amount
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY id ASC
                """,
                (start_date, end_date),
            )
            return [
                Expense(
                    id=row["id"],
                    date=row["date"],
                    amount=row["amount"],
                    category=row["category"],
                    subcategory=row["subcategory"] or "",
                    note=row["note"] or "",
                    original_currency=row["original_currency"] or "USD",
                    usd_amount=row["usd_amount"],
                )
                for row in rows
            ]
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to list expenses: {e}") from e

    def get_by_category(self, start_date: str, end_date: str, category: str) -> list[Expense]:
        """Get expenses for a specific category within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: Category name
            
        Returns:
            List of Expense objects matching the category
            
        Raises:
            DatabaseError: If query fails
        """
        try:
            rows = self._db.execute_query(
                """
                SELECT id, date, amount, category, subcategory, note, 
                       original_currency, usd_amount
                FROM expenses
                WHERE date BETWEEN ? AND ? AND category = ?
                ORDER BY id ASC
                """,
                (start_date, end_date, category),
            )
            return [
                Expense(
                    id=row["id"],
                    date=row["date"],
                    amount=row["amount"],
                    category=row["category"],
                    subcategory=row["subcategory"] or "",
                    note=row["note"] or "",
                    original_currency=row["original_currency"] or "USD",
                    usd_amount=row["usd_amount"],
                )
                for row in rows
            ]
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get expenses by category: {e}") from e
