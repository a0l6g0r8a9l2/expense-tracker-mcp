"""Pytest configuration and reusable fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from app.config.settings import Settings
from app.database.db import DatabaseManager
from app.database.repositories import ExpenseRepository
from app.models.expense import Expense
from app.services.currency_service import CurrencyService
from app.services.expense_service import ExpenseService
from app.services.summary_service import SummaryService


@pytest.fixture
def temp_db() -> Generator[Path, None, None]:
    """Create a temporary database for testing.
    
    Yields:
        Path to temporary database file
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_expenses.db"
        yield db_path


@pytest.fixture
def db_manager(temp_db: Path) -> DatabaseManager:
    """Create a database manager with temporary database.
    
    Args:
        temp_db: Temporary database path
        
    Returns:
        Initialized DatabaseManager
    """
    manager = DatabaseManager(temp_db)
    manager.init_db()
    return manager


@pytest.fixture
def repository(db_manager: DatabaseManager) -> ExpenseRepository:
    """Create an expense repository.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        ExpenseRepository instance
    """
    return ExpenseRepository(db_manager)


@pytest.fixture
def currency_service() -> CurrencyService:
    """Create a currency service (without API key for testing).
    
    Returns:
        CurrencyService instance
    """
    return CurrencyService(api_key=None, default_currency="USD")


@pytest.fixture
def temp_categories_file() -> Generator[Path, None, None]:
    """Create a temporary categories.json file for testing.
    
    Yields:
        Path to temporary categories file
    """
    categories = {
        "food": ["groceries", "dining_out"],
        "transport": ["fuel", "public_transport"],
        "housing": ["rent"],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        categories_path = Path(tmpdir) / "categories.json"
        with open(categories_path, "w") as f:
            json.dump(categories, f)
        yield categories_path


@pytest.fixture
def expense_service(
    repository: ExpenseRepository,
    currency_service: CurrencyService,
    temp_categories_file: Path,
) -> ExpenseService:
    """Create an expense service for testing.
    
    Args:
        repository: ExpenseRepository instance
        currency_service: CurrencyService instance
        temp_categories_file: Temporary categories file path
        
    Returns:
        ExpenseService instance
    """
    return ExpenseService(
        repository=repository,
        currency_service=currency_service,
        categories_path=str(temp_categories_file),
        default_currency="USD",
    )


@pytest.fixture
def summary_service(
    repository: ExpenseRepository, temp_categories_file: Path
) -> SummaryService:
    """Create a summary service for testing.
    
    Args:
        repository: ExpenseRepository instance
        temp_categories_file: Temporary categories file path
        
    Returns:
        SummaryService instance
    """
    with open(temp_categories_file) as f:
        categories = json.load(f)
    return SummaryService(repository, categories)


@pytest.fixture
def sample_expense() -> Expense:
    """Create a sample expense for testing.
    
    Returns:
        Sample Expense object
    """
    return Expense(
        id=1,
        date="2026-04-15",
        amount=100.00,
        category="food",
        subcategory="groceries",
        note="Weekly shopping",
        original_currency="USD",
        usd_amount=100.00,
    )
