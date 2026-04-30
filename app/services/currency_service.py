"""Currency exchange rate service."""

from __future__ import annotations

from typing import Optional

import requests

from app.constants import (
    DECIMAL_PLACES,
    EXCHANGE_RATE_API_BASE_URL,
    EXCHANGE_RATE_API_TIMEOUT,
)
from app.exceptions import ExchangeRateError
from app.logger import get_logger

logger = get_logger(__name__)


class ExchangeRateCache:
    """Simple in-memory cache for exchange rates."""

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._cache: dict[str, float] = {}

    def get(self, key: str) -> Optional[float]:
        """Get cached exchange rate.
        
        Args:
            key: Cache key (format: "FROM_TO")
            
        Returns:
            Cached rate or None if not in cache
        """
        return self._cache.get(key)

    def set(self, key: str, rate: float) -> None:
        """Store exchange rate in cache.
        
        Args:
            key: Cache key (format: "FROM_TO")
            rate: Exchange rate value
        """
        self._cache[key] = rate

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


class CurrencyService:
    """Service for currency conversion using exchangerate-api.com."""

    def __init__(self, api_key: Optional[str], default_currency: str = "USD") -> None:
        """Initialize currency service.
        
        Args:
            api_key: API key for exchangerate-api.com (optional)
            default_currency: Default target currency for conversions
        """
        self._api_key = api_key
        self._default_currency = default_currency
        self._cache = ExchangeRateCache()

    def get_exchange_rate(
        self, from_currency: str, to_currency: Optional[str] = None
    ) -> Optional[float]:
        """Fetch exchange rate from API with caching.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code (defaults to default_currency)
            
        Returns:
            Exchange rate as float, or None if unavailable
        """
        if to_currency is None:
            to_currency = self._default_currency

        # Normalize currency codes
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()

        # Same currency conversion rate is always 1.0
        if from_currency == to_currency:
            return 1.0

        # Check cache
        cache_key = f"{from_currency}_{to_currency}"
        cached_rate = self._cache.get(cache_key)
        if cached_rate is not None:
            return cached_rate

        # API key required for actual conversion
        if not self._api_key:
            logger.warning(
                f"EXCHANGE_RATE_API_KEY not set. Cannot fetch {from_currency} → {to_currency} rate."
            )
            return None

        # Fetch from API
        try:
            url = f"{EXCHANGE_RATE_API_BASE_URL}/{self._api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url, timeout=EXCHANGE_RATE_API_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            if data.get("result") != "success":
                error_type = data.get("error-type", "Unknown error")
                logger.warning(
                    f"Exchange rate API error for {from_currency}→{to_currency}: {error_type}"
                )
                return None

            rate = data.get("conversion_rate")
            if rate is None:
                logger.warning(
                    f"No conversion_rate in API response for {from_currency}→{to_currency}"
                )
                return None

            # Cache the rate
            self._cache.set(cache_key, rate)
            return rate

        except requests.exceptions.Timeout:
            logger.warning(f"Exchange rate API timeout for {from_currency}→{to_currency}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Exchange rate API error: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse exchange rate response: {e}")
            return None

    def convert_currency(
        self, amount: float, source_currency: str, target_currency: Optional[str] = None
    ) -> Optional[float]:
        """Convert amount from source currency to target currency.
        
        Args:
            amount: Amount to convert
            source_currency: Source currency code
            target_currency: Target currency code (defaults to default_currency)
            
        Returns:
            Converted amount rounded to DECIMAL_PLACES, or None if conversion fails
        """
        if amount <= 0:
            return None

        rate = self.get_exchange_rate(source_currency, target_currency)
        if rate is None:
            return None

        converted = amount * rate
        return round(converted, DECIMAL_PLACES)

    def clear_cache(self) -> None:
        """Clear exchange rate cache."""
        self._cache.clear()
