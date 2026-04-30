"""Application constants and configuration values."""

import re
from typing import Final

# Date and time constants
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATE_PATTERN: Final[re.Pattern] = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Currency constants
CURRENCY_PATTERN: Final[re.Pattern] = re.compile(r"^[A-Z]{3}$")
DEFAULT_CURRENCY: Final[str] = "USD"

# Amount validation constants
MIN_AMOUNT: Final[float] = 0.01
MAX_AMOUNT: Final[float] = 999_999_999.99

# Precision constants
DECIMAL_PLACES: Final[int] = 2

# API constants
EXCHANGE_RATE_API_TIMEOUT: Final[int] = 5  # seconds
EXCHANGE_RATE_API_BASE_URL: Final[str] = "https://v6.exchangerate-api.com/v6"
