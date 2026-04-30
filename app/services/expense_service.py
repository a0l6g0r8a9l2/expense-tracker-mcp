"""Expense service for business logic."""

from __future__ import annotations

import json
from typing import Optional

from app.database.repositories import ExpenseRepository
from app.exceptions import ValidationError
from app.logger import get_logger
from app.models.expense import AddExpenseRequest, Expense, ExpenseResponse
from app.services.currency_service import CurrencyService
from app.validators import (
    validate_amount,
    validate_category,
    validate_currency,
    validate_date,
    validate_note,
    validate_subcategory,
)

logger = get_logger(__name__)


class ExpenseService:
    """Service for managing expense operations with validation and conversion."""

    def __init__(
        self,
        repository: ExpenseRepository,
        currency_service: CurrencyService,
        categories_path: str,
        default_currency: str = "USD",
    ) -> None:
        """Initialize expense service.
        
        Args:
            repository: Data access layer for expenses
            currency_service: Currency conversion service
            categories_path: Path to categories.json file
            default_currency: Default currency for amounts
        """
        self._repository = repository
        self._currency_service = currency_service
        self._default_currency = default_currency
        self._valid_categories = self._load_categories(categories_path)

    def _load_categories(self, categories_path: str) -> dict:
        """Load valid categories from JSON file.
        
        Args:
            categories_path: Path to categories.json
            
        Returns:
            Dictionary of valid categories
            
        Raises:
            ValidationError: If categories file cannot be loaded
        """
        try:
            with open(categories_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValidationError(f"Failed to load categories: {e}") from e

    def add_expense(self, request: AddExpenseRequest) -> ExpenseResponse:
        """Add a new expense with validation and currency conversion.
        
        Args:
            request: AddExpenseRequest with expense data
            
        Returns:
            ExpenseResponse with status and result details
        """
        try:
            # Validate all inputs
            validate_date(request.date)
            validate_amount(request.amount)
            
            currency = validate_currency(request.currency or self._default_currency)
            category = validate_category(request.category, self._valid_categories)
            subcategory = validate_subcategory(
                request.subcategory, category, self._valid_categories
            )
            note = validate_note(request.note)

            # Convert to USD if needed
            usd_amount: Optional[float] = None
            if currency != "USD":
                usd_amount = self._currency_service.convert_currency(
                    request.amount, currency, "USD"
                )
            else:
                usd_amount = request.amount

            # Create expense object
            expense = Expense(
                id=0,  # Will be set by database
                date=request.date,
                amount=request.amount,
                category=category,
                subcategory=subcategory,
                note=note,
                original_currency=currency,
                usd_amount=usd_amount,
            )

            # Save to database
            expense_id = self._repository.add(expense)

            return ExpenseResponse(
                status="ok",
                id=expense_id,
                original_amount=request.amount,
                original_currency=currency,
                usd_amount=usd_amount,
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return ExpenseResponse(status="error", message=str(e))
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return ExpenseResponse(status="error", message=str(e))

    def get_categories(self) -> dict:
        """Get valid categories.
        
        Returns:
            Dictionary of valid categories and subcategories
        """
        return self._valid_categories
