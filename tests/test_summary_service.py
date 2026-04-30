"""Tests for summary service."""

import pytest

from app.models.expense import Expense
from app.services.summary_service import SummaryService


class TestCalculateSummary:
    """Tests for expense summary calculation."""

    def test_single_category_summary(
        self, repository, summary_service: SummaryService
    ) -> None:
        """Summary for single category should calculate total."""
        expense1 = Expense(
            id=0,
            date="2026-04-15",
            amount=50.00,
            category="food",
            original_currency="USD",
            usd_amount=50.00,
        )
        expense2 = Expense(
            id=0,
            date="2026-04-16",
            amount=75.00,
            category="food",
            original_currency="USD",
            usd_amount=75.00,
        )
        
        repository.add(expense1)
        repository.add(expense2)
        
        summary = summary_service.calculate_summary("2026-04-14", "2026-04-20")
        
        assert len(summary) == 1
        assert summary[0].category == "food"
        assert summary[0].total_amount == 125.00

    def test_multiple_categories_summary(
        self, repository, summary_service: SummaryService
    ) -> None:
        """Summary should aggregate each category separately."""
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
        
        summary = summary_service.calculate_summary("2026-04-14", "2026-04-20")
        
        assert len(summary) == 2
        assert summary[0].category == "food"
        assert summary[0].total_amount == 100.00
        assert summary[1].category == "transport"
        assert summary[1].total_amount == 50.00

    def test_category_filter(
        self, repository, summary_service: SummaryService
    ) -> None:
        """Summary with category filter should return only that category."""
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
        
        summary = summary_service.calculate_summary("2026-04-14", "2026-04-20", category="food")
        
        assert len(summary) == 1
        assert summary[0].category == "food"

    def test_empty_date_range(self, repository, summary_service: SummaryService) -> None:
        """Summary for empty date range should return empty list."""
        expense = Expense(
            id=0,
            date="2026-04-15",
            amount=100.00,
            category="food",
            original_currency="USD",
            usd_amount=100.00,
        )
        
        repository.add(expense)
        
        summary = summary_service.calculate_summary("2026-05-01", "2026-05-31")
        
        assert len(summary) == 0

    def test_multi_currency_aggregation(
        self, repository, summary_service: SummaryService
    ) -> None:
        """Multi-currency expenses should use USD conversion."""
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
            amount=85.00,
            category="food",
            original_currency="EUR",
            usd_amount=95.00,
        )
        
        repository.add(expense1)
        repository.add(expense2)
        
        summary = summary_service.calculate_summary("2026-04-14", "2026-04-20")
        
        assert len(summary) == 1
        assert summary[0].category == "food"
        # Should report USD totals when multiple currencies
        assert summary[0].total_amount == 195.00
        assert summary[0].original_currency == "USD (converted)"
