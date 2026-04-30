"""Input validation functions for expense tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.constants import (
    CURRENCY_PATTERN,
    DATE_FORMAT,
    DATE_PATTERN,
    MAX_AMOUNT,
    MIN_AMOUNT,
)
from app.exceptions import ValidationError


def validate_date(date_str: str) -> None:
    """Validate date string format (YYYY-MM-DD) and actual date validity.
    
    Args:
        date_str: Date string to validate
        
    Raises:
        ValidationError: If date format or value is invalid
    """
    if not date_str:
        raise ValidationError("Date cannot be empty")
    
    if not DATE_PATTERN.match(date_str):
        raise ValidationError(f"Date must be in format {DATE_FORMAT}, got: {date_str}")
    
    try:
        datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as e:
        raise ValidationError(f"Invalid date value: {date_str}") from e


def validate_amount(amount: float) -> None:
    """Validate expense amount is positive and within bounds.
    
    Args:
        amount: Amount to validate
        
    Raises:
        ValidationError: If amount is invalid
    """
    if not isinstance(amount, (int, float)):
        raise ValidationError(f"Amount must be a number, got: {type(amount).__name__}")
    
    if amount < MIN_AMOUNT or amount > MAX_AMOUNT:
        raise ValidationError(f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT}, got: {amount}")


def validate_currency(currency: str) -> str:
    """Validate currency code format (3 uppercase letters).
    
    Args:
        currency: Currency code to validate
        
    Returns:
        Normalized (uppercase) currency code
        
    Raises:
        ValidationError: If currency code is invalid
    """
    if not currency:
        raise ValidationError("Currency cannot be empty")
    
    normalized = currency.upper().strip()
    
    if not CURRENCY_PATTERN.match(normalized):
        raise ValidationError(f"Currency must be 3 uppercase letters, got: {currency}")
    
    return normalized


def validate_category(category: str, valid_categories: dict) -> str:
    """Validate category exists in valid categories.
    
    Args:
        category: Category to validate
        valid_categories: Dictionary of valid categories
        
    Returns:
        Normalized category
        
    Raises:
        ValidationError: If category is invalid
    """
    if not category:
        raise ValidationError("Category cannot be empty")
    
    normalized = category.lower().strip()
    
    if normalized not in valid_categories:
        available = ", ".join(sorted(valid_categories.keys()))
        raise ValidationError(f"Invalid category '{category}'. Available: {available}")
    
    return normalized


def validate_subcategory(
    subcategory: Optional[str], category: str, valid_categories: dict
) -> str:
    """Validate subcategory exists for given category.
    
    Args:
        subcategory: Subcategory to validate (optional)
        category: Parent category
        valid_categories: Dictionary of valid categories and subcategories
        
    Returns:
        Normalized subcategory (empty string if not provided)
        
    Raises:
        ValidationError: If subcategory is invalid
    """
    if not subcategory:
        return ""
    
    normalized = subcategory.lower().strip()
    valid_subs = valid_categories.get(category, [])
    
    if normalized not in valid_subs:
        available = ", ".join(sorted(valid_subs))
        raise ValidationError(
            f"Invalid subcategory '{subcategory}' for category '{category}'. "
            f"Available: {available}"
        )
    
    return normalized


def validate_note(note: Optional[str]) -> str:
    """Validate and normalize note field.
    
    Args:
        note: Note to validate (optional)
        
    Returns:
        Normalized note (empty string if not provided)
    """
    if not note:
        return ""
    
    return note.strip()
