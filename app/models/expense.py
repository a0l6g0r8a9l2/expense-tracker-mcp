"""Data models and dataclasses for expense tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Expense:
    """Represents an expense record from the database."""

    id: int
    date: str
    amount: float
    category: str
    subcategory: str = ""
    note: str = ""
    original_currency: str = "USD"
    usd_amount: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "subcategory": self.subcategory,
            "note": self.note,
            "original_currency": self.original_currency,
            "usd_amount": self.usd_amount,
        }


@dataclass
class AddExpenseRequest:
    """Request model for adding a new expense (input validation)."""

    date: str
    amount: float
    category: str
    subcategory: str = ""
    note: str = ""
    currency: str = "USD"


@dataclass
class ExpenseResponse:
    """Response model for add expense operation."""

    status: str  # "ok" or "error"
    id: Optional[int] = None
    original_amount: Optional[float] = None
    original_currency: Optional[str] = None
    usd_amount: Optional[float] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = {"status": self.status}
        if self.id is not None:
            data["id"] = self.id
        if self.original_amount is not None:
            data["original_amount"] = self.original_amount
        if self.original_currency is not None:
            data["original_currency"] = self.original_currency
        if self.usd_amount is not None:
            data["usd_amount"] = self.usd_amount
        if self.message is not None:
            data["message"] = self.message
        return data


@dataclass
class SummaryRow:
    """Expense summary aggregated by category."""

    category: str
    total_amount: float
    original_currency: Optional[str] = None
    total_usd_amount: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        data = {
            "category": self.category,
            "total_amount": self.total_amount,
        }
        if self.original_currency is not None:
            data["original_currency"] = self.original_currency
        if self.total_usd_amount is not None:
            data["total_usd_amount"] = self.total_usd_amount
        return data
