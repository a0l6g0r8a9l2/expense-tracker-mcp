"""Configuration settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.constants import DEFAULT_CURRENCY
from app.exceptions import ConfigurationError
from dotenv import load_dotenv


@dataclass
class Settings:
    """Application settings loaded from environment and defaults."""

    default_currency: str
    exchange_rate_api_key: str | None
    db_path: Path
    categories_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables.
        
        Returns:
            Settings instance
            
        Raises:
            ConfigurationError: If required paths don't exist
        """
        load_dotenv()
        
        # Determine project root directory (go up from app/config/settings.py to root)
        project_root = Path(__file__).parent.parent.parent
        
        # Database path
        db_path = project_root / "expenses.db"
        
        # Categories path
        categories_path = project_root / "categories.json"
        if not categories_path.exists():
            raise ConfigurationError(
                f"Categories file not found at {categories_path}"
            )
        
        return cls(
            default_currency=os.getenv("DEFAULT_CURRENCY", DEFAULT_CURRENCY),
            exchange_rate_api_key=os.getenv("EXCHANGE_RATE_API_KEY"),
            db_path=db_path,
            categories_path=categories_path,
        )
