"""Tests for data models."""

from app.models.expense import AddExpenseRequest, Expense, ExpenseResponse, SummaryRow


class TestExpenseModel:
    """Tests for Expense model."""

    def test_expense_to_dict(self) -> None:
        """Expense should convert to dictionary."""
        expense = Expense(
            id=1,
            date="2026-04-15",
            amount=100.00,
            category="food",
            subcategory="groceries",
            note="Shopping",
            original_currency="USD",
            usd_amount=100.00,
        )
        
        result = expense.to_dict()
        
        assert result["id"] == 1
        assert result["date"] == "2026-04-15"
        assert result["amount"] == 100.00
        assert result["category"] == "food"
        assert result["subcategory"] == "groceries"
        assert result["note"] == "Shopping"


class TestAddExpenseRequest:
    """Tests for AddExpenseRequest model."""

    def test_create_request_with_defaults(self) -> None:
        """AddExpenseRequest should accept defaults."""
        request = AddExpenseRequest(
            date="2026-04-15",
            amount=100.00,
            category="food",
        )
        
        assert request.date == "2026-04-15"
        assert request.amount == 100.00
        assert request.category == "food"
        assert request.subcategory == ""
        assert request.note == ""
        assert request.currency == "USD"


class TestExpenseResponse:
    """Tests for ExpenseResponse model."""

    def test_success_response(self) -> None:
        """Success response should include all data."""
        response = ExpenseResponse(
            status="ok",
            id=1,
            original_amount=100.00,
            original_currency="USD",
            usd_amount=100.00,
        )
        
        result = response.to_dict()
        
        assert result["status"] == "ok"
        assert result["id"] == 1
        assert result["original_amount"] == 100.00
        assert result["original_currency"] == "USD"
        assert result["usd_amount"] == 100.00

    def test_error_response(self) -> None:
        """Error response should include message."""
        response = ExpenseResponse(status="error", message="Invalid input")
        
        result = response.to_dict()
        
        assert result["status"] == "error"
        assert result["message"] == "Invalid input"


class TestSummaryRow:
    """Tests for SummaryRow model."""

    def test_summary_row_single_currency(self) -> None:
        """Summary row with single currency should include it."""
        row = SummaryRow(
            category="food",
            total_amount=150.00,
            original_currency="USD",
        )
        
        result = row.to_dict()
        
        assert result["category"] == "food"
        assert result["total_amount"] == 150.00
        assert result["original_currency"] == "USD"

    def test_summary_row_with_usd_amount(self) -> None:
        """Summary row should include USD amount when present."""
        row = SummaryRow(
            category="food",
            total_amount=150.00,
            original_currency="EUR",
            total_usd_amount=170.00,
        )
        
        result = row.to_dict()
        
        assert result["total_usd_amount"] == 170.00
