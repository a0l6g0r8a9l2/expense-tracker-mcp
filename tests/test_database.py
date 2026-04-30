"""Tests for database operations."""

import pytest

from app.database.repositories import ExpenseRepository
from app.exceptions import DatabaseError
from app.models.expense import Expense


class TestExpenseRepository:
    """Tests for ExpenseRepository."""

    def test_add_expense(self, repository: ExpenseRepository) -> None:
        """Adding an expense should return a valid ID."""
        expense = Expense(
            id=0,
            date="2026-04-15",
            amount=100.00,
            category="food",
            subcategory="groceries",
            note="Shopping",
            original_currency="USD",
            usd_amount=100.00,
        )
        
        expense_id = repository.add(expense)
        
        assert expense_id > 0

    def test_list_expenses(self, repository: ExpenseRepository) -> None:
        """Listing expenses in date range should return added expenses."""
        expense1 = Expense(
            id=0,
            date="2026-04-14",
            amount=50.00,
            category="food",
            original_currency="USD",
            usd_amount=50.00,
        )
        expense2 = Expense(
            id=0,
            date="2026-04-15",
            amount=100.00,
            category="transport",
            original_currency="USD",
            usd_amount=100.00,
        )
        
        repository.add(expense1)
        repository.add(expense2)
        
        results = repository.list("2026-04-14", "2026-04-16")
        
        assert len(results) == 2
        assert results[0].amount == 50.00
        assert results[1].amount == 100.00

    def test_list_expenses_empty_range(self, repository: ExpenseRepository) -> None:
        """Listing expenses in empty range should return empty list."""
        expense = Expense(
            id=0,
            date="2026-04-15",
            amount=100.00,
            category="food",
            original_currency="USD",
            usd_amount=100.00,
        )
        
        repository.add(expense)
        
        results = repository.list("2026-05-01", "2026-05-31")
        
        assert len(results) == 0

    def test_get_by_category(self, repository: ExpenseRepository) -> None:
        """Getting expenses by category should return only that category."""
        expense1 = Expense(
            id=0,
            date="2026-04-15",
            amount=100.00,
            category="food",
            original_currency="USD",
            usd_amount=100.00,
        )
        expense2 = Expense(
            id=0,
            date="2026-04-15",
            amount=50.00,
            category="transport",
            original_currency="USD",
            usd_amount=50.00,
        )
        
        repository.add(expense1)
        repository.add(expense2)
        
        results = repository.get_by_category("2026-04-14", "2026-04-16", "food")
        
        assert len(results) == 1
        assert results[0].category == "food"
        assert results[0].amount == 100.00

    def test_preserves_expense_data(self, repository: ExpenseRepository) -> None:
        """Repository should preserve all expense data."""
        original_expense = Expense(
            id=0,
            date="2026-04-15",
            amount=123.45,
            category="food",
            subcategory="dining_out",
            note="Restaurant XYZ",
            original_currency="EUR",
            usd_amount=135.00,
        )
        
        expense_id = repository.add(original_expense)
        results = repository.list("2026-04-14", "2026-04-16")
        
        assert len(results) == 1
        retrieved = results[0]
        assert retrieved.amount == 123.45
        assert retrieved.category == "food"
        assert retrieved.subcategory == "dining_out"
        assert retrieved.note == "Restaurant XYZ"
        assert retrieved.original_currency == "EUR"
        assert retrieved.usd_amount == 135.00
