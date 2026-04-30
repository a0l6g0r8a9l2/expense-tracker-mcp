"""Tests for expense service."""

import pytest

from app.exceptions import ValidationError
from app.models.expense import AddExpenseRequest
from app.services.expense_service import ExpenseService


class TestAddExpense:
    """Tests for adding expenses."""

    def test_add_valid_expense(self, expense_service: ExpenseService) -> None:
        """Adding a valid expense should succeed."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=100.00,
            category="food",
            subcategory="groceries",
            note="Weekly shopping",
            currency="USD",
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "ok"
        assert response.id is not None
        assert response.original_amount == 100.00
        assert response.original_currency == "USD"
        assert response.usd_amount == 100.00

    def test_add_expense_invalid_date(self, expense_service: ExpenseService) -> None:
        """Adding expense with invalid date should fail."""
        request = AddExpenseRequest(
            date="2026-13-01",  # Invalid month
            amount=100.00,
            category="food",
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "error"
        assert response.message is not None

    def test_add_expense_invalid_amount(self, expense_service: ExpenseService) -> None:
        """Adding expense with invalid amount should fail."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=-50.00,  # Negative
            category="food",
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "error"

    def test_add_expense_invalid_category(self, expense_service: ExpenseService) -> None:
        """Adding expense with invalid category should fail."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=100.00,
            category="invalid_category",
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "error"

    def test_add_expense_default_currency(self, expense_service: ExpenseService) -> None:
        """Adding expense without currency should use default."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=100.00,
            category="food",
            currency="",  # Empty, should use default
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "ok"
        assert response.original_currency == "USD"

    def test_add_expense_with_subcategory(self, expense_service: ExpenseService) -> None:
        """Adding expense with valid subcategory should succeed."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=50.00,
            category="food",
            subcategory="dining_out",
        )
        
        response = expense_service.add_expense(request)
        
        assert response.status == "ok"


class TestGetCategories:
    """Tests for getting categories."""

    def test_get_categories(self, expense_service: ExpenseService) -> None:
        """Getting categories should return valid structure."""
        categories = expense_service.get_categories()
        
        assert isinstance(categories, dict)
        assert "food" in categories
        assert "transport" in categories
        assert isinstance(categories["food"], list)
