"""Custom exceptions for the expense tracker application."""


class ExpenseTrackerError(Exception):
    """Base exception for all expense tracker errors."""

    pass


class ValidationError(ExpenseTrackerError):
    """Raised when input validation fails."""

    pass


class DatabaseError(ExpenseTrackerError):
    """Raised when database operations fail."""

    pass


class ExchangeRateError(ExpenseTrackerError):
    """Raised when exchange rate API operations fail."""

    pass


class ConfigurationError(ExpenseTrackerError):
    """Raised when configuration is invalid or missing."""

    pass
