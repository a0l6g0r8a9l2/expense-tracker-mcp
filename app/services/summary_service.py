"""Summary and aggregation service for expense analysis."""

from __future__ import annotations

from typing import Optional

from app.database.repositories import ExpenseRepository
from app.exceptions import ValidationError
from app.logger import get_logger
from app.models.expense import SummaryRow
from app.validators import validate_category, validate_date

logger = get_logger(__name__)


class SummaryService:
    """Service for generating expense summaries and aggregations."""

    def __init__(self, repository: ExpenseRepository, valid_categories: dict) -> None:
        """Initialize summary service.
        
        Args:
            repository: Data access layer for expenses
            valid_categories: Dictionary of valid categories
        """
        self._repository = repository
        self._valid_categories = valid_categories

    def calculate_summary(
        self, start_date: str, end_date: str, category: Optional[str] = None
    ) -> list[SummaryRow]:
        """Calculate expense summary by category within date range.
        
        Properly handles multi-currency expenses by using USD conversion values
        when available.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            category: Optional category filter
            
        Returns:
            List of SummaryRow objects with aggregated amounts
            
        Raises:
            ValidationError: If dates or category are invalid
        """
        try:
            # Validate dates
            validate_date(start_date)
            validate_date(end_date)

            # Validate category if provided
            if category:
                category = validate_category(category, self._valid_categories)

            # Get expenses from database
            expenses = self._repository.list(start_date, end_date)

            # Aggregate by category
            summary_dict: dict[str, dict] = {}

            for expense in expenses:
                # Filter by category if specified
                if category and expense.category != category:
                    continue

                cat = expense.category
                if cat not in summary_dict:
                    summary_dict[cat] = {
                        "category": cat,
                        "total_amount": 0.0,
                        "total_usd_amount": 0.0,
                        "original_currency": expense.original_currency,
                        "has_multiple_currencies": False,
                    }

                # Track if we have multiple currencies
                if summary_dict[cat]["original_currency"] != expense.original_currency:
                    summary_dict[cat]["has_multiple_currencies"] = True

                # Sum amounts
                summary_dict[cat]["total_amount"] += expense.amount
                if expense.usd_amount is not None:
                    summary_dict[cat]["total_usd_amount"] += expense.usd_amount

            # Convert to SummaryRow objects
            results: list[SummaryRow] = []
            for summary_data in summary_dict.values():
                # When there are multiple currencies, report USD total
                # Otherwise report original currency total
                if summary_data["has_multiple_currencies"]:
                    results.append(
                        SummaryRow(
                            category=summary_data["category"],
                            total_amount=summary_data["total_usd_amount"],
                            original_currency="USD (converted)",
                            total_usd_amount=summary_data["total_usd_amount"],
                        )
                    )
                else:
                    results.append(
                        SummaryRow(
                            category=summary_data["category"],
                            total_amount=summary_data["total_amount"],
                            original_currency=summary_data["original_currency"],
                            total_usd_amount=(
                                summary_data["total_usd_amount"]
                                if summary_data["total_usd_amount"] > 0
                                else None
                            ),
                        )
                    )

            # Sort by category name
            results.sort(key=lambda x: x.category)
            return results

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error calculating summary: {e}")
            raise ValidationError(f"Failed to calculate summary: {e}") from e
