"""MCP tools registration and FastMCP integration."""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from app.config.settings import Settings
from app.database.db import DatabaseManager
from app.database.repositories import ExpenseRepository
from app.models.expense import AddExpenseRequest
from app.services.currency_service import CurrencyService
from app.services.expense_service import ExpenseService
from app.services.summary_service import SummaryService

# Initialize global instances
_settings: Settings | None = None
_mcp: FastMCP | None = None
_db_manager: DatabaseManager | None = None
_repository: ExpenseRepository | None = None
_currency_service: CurrencyService | None = None
_expense_service: ExpenseService | None = None
_summary_service: SummaryService | None = None


def initialize_services(mcp_instance: FastMCP) -> None:
    """Initialize all application services.
    
    Args:
        mcp_instance: FastMCP instance for tool registration
    """
    global _settings, _mcp, _db_manager, _repository, _currency_service
    global _expense_service, _summary_service

    _mcp = mcp_instance
    _settings = Settings.from_env()
    _db_manager = DatabaseManager(_settings.db_path)
    _db_manager.init_db()
    _repository = ExpenseRepository(_db_manager)
    _currency_service = CurrencyService(
        _settings.exchange_rate_api_key, _settings.default_currency
    )
    _expense_service = ExpenseService(
        _repository,
        _currency_service,
        str(_settings.categories_path),
        _settings.default_currency,
    )
    _summary_service = SummaryService(_repository, _expense_service.get_categories())


def register_tools(mcp: FastMCP) -> None:
    """Register all MCP tools.
    
    Args:
        mcp: FastMCP instance
    """
    initialize_services(mcp)

    @mcp.tool()
    def add_expense(
        date: str,
        amount: float,
        category: str,
        subcategory: str = "",
        note: str = "",
        currency: str = "",
    ) -> dict[str, Any]:
        """Add a new expense entry to the database with optional currency conversion to USD.

        Args:
            date: Expense date (YYYY-MM-DD format)
            amount: Expense amount in the original currency
            category: Expense category
            subcategory: Expense subcategory (optional)
            note: Expense description (optional)
            currency: Currency code (e.g., "USD", "EUR", "GBP"). If not provided, uses default from config

        Returns:
            Dictionary with status, id, original_amount, original_currency, and usd_amount
        """
        request = AddExpenseRequest(
            date=date,
            amount=amount,
            category=category,
            subcategory=subcategory,
            note=note,
            currency=currency or _settings.default_currency,
        )
        response = _expense_service.add_expense(request)
        return response.to_dict()

    @mcp.tool()
    def list_expenses(start_date: str, end_date: str) -> list[dict[str, Any]]:
        """List expense entries within an inclusive date range with currency information."""
        expenses = _repository.list(start_date, end_date)
        return [exp.to_dict() for exp in expenses]

    @mcp.tool()
    def summarize(start_date: str, end_date: str, category: str = "") -> list[dict[str, Any]]:
        """Summarize expenses by category within an inclusive date range.

        Args:
            start_date: Start date (inclusive, YYYY-MM-DD format)
            end_date: End date (inclusive, YYYY-MM-DD format)
            category: Optional filter by category

        Returns:
            List of dictionaries with category and total_amount (or total_usd_amount if converted)
        """
        summary_rows = _summary_service.calculate_summary(
            start_date, end_date, category or None
        )
        return [row.to_dict() for row in summary_rows]

    @mcp.resource("expense://categories", mime_type="application/json")
    def categories() -> str:
        """Get all valid expense categories and subcategories."""
        with open(_settings.categories_path, "r", encoding="utf-8") as f:
            return f.read()
