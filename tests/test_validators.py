"""Tests for input validators."""

import pytest

from app.exceptions import ValidationError
from app.validators import (
    validate_amount,
    validate_category,
    validate_currency,
    validate_date,
    validate_note,
    validate_subcategory,
)


class TestValidateDate:
    """Tests for date validation."""

    def test_valid_date(self) -> None:
        """Valid date should pass."""
        validate_date("2026-04-15")  # Should not raise

    def test_invalid_format(self) -> None:
        """Invalid format should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("2026-4-15")  # Missing leading zero

    def test_empty_date(self) -> None:
        """Empty date should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("")

    def test_invalid_month(self) -> None:
        """Invalid month should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_date("2026-13-01")


class TestValidateAmount:
    """Tests for amount validation."""

    def test_valid_amount(self) -> None:
        """Valid amount should pass."""
        validate_amount(100.50)  # Should not raise

    def test_zero_amount(self) -> None:
        """Zero amount should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_amount(0)

    def test_negative_amount(self) -> None:
        """Negative amount should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_amount(-50.00)

    def test_non_numeric_amount(self) -> None:
        """Non-numeric amount should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_amount("100")  # type: ignore

    def test_too_large_amount(self) -> None:
        """Amount exceeding max should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_amount(1_000_000_000)


class TestValidateCurrency:
    """Tests for currency validation."""

    def test_valid_currency(self) -> None:
        """Valid currency code should return uppercase."""
        result = validate_currency("usd")
        assert result == "USD"

    def test_uppercase_currency(self) -> None:
        """Uppercase currency should pass through."""
        result = validate_currency("EUR")
        assert result == "EUR"

    def test_invalid_length(self) -> None:
        """Invalid length should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_currency("US")

    def test_empty_currency(self) -> None:
        """Empty currency should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_currency("")

    def test_lowercase_with_spaces(self) -> None:
        """Lowercase currency with spaces should be normalized."""
        result = validate_currency("  gbp  ")
        assert result == "GBP"


class TestValidateCategory:
    """Tests for category validation."""

    def test_valid_category(self) -> None:
        """Valid category should return normalized value."""
        categories = {"food": [], "transport": []}
        result = validate_category("Food", categories)
        assert result == "food"

    def test_invalid_category(self) -> None:
        """Invalid category should raise ValidationError."""
        categories = {"food": [], "transport": []}
        with pytest.raises(ValidationError):
            validate_category("invalid", categories)

    def test_empty_category(self) -> None:
        """Empty category should raise ValidationError."""
        categories = {"food": []}
        with pytest.raises(ValidationError):
            validate_category("", categories)


class TestValidateSubcategory:
    """Tests for subcategory validation."""

    def test_valid_subcategory(self) -> None:
        """Valid subcategory should return normalized value."""
        categories = {"food": ["groceries", "dining_out"]}
        result = validate_subcategory("Groceries", "food", categories)
        assert result == "groceries"

    def test_empty_subcategory(self) -> None:
        """Empty subcategory should return empty string."""
        categories = {"food": ["groceries"]}
        result = validate_subcategory("", "food", categories)
        assert result == ""

    def test_invalid_subcategory(self) -> None:
        """Invalid subcategory should raise ValidationError."""
        categories = {"food": ["groceries"]}
        with pytest.raises(ValidationError):
            validate_subcategory("invalid_sub", "food", categories)


class TestValidateNote:
    """Tests for note validation."""

    def test_valid_note(self) -> None:
        """Valid note should return normalized value."""
        result = validate_note("  Sample note  ")
        assert result == "Sample note"

    def test_empty_note(self) -> None:
        """Empty note should return empty string."""
        result = validate_note("")
        assert result == ""

    def test_none_note(self) -> None:
        """None note should return empty string."""
        result = validate_note(None)
        assert result == ""
