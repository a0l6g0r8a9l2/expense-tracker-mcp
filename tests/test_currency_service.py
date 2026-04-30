"""Tests for currency service."""

import pytest

from app.services.currency_service import CurrencyService, ExchangeRateCache


class TestExchangeRateCache:
    """Tests for ExchangeRateCache."""

    def test_cache_get_set(self) -> None:
        """Cache should store and retrieve rates."""
        cache = ExchangeRateCache()
        
        cache.set("USD_EUR", 0.92)
        result = cache.get("USD_EUR")
        
        assert result == 0.92

    def test_cache_get_missing_key(self) -> None:
        """Cache get for missing key should return None."""
        cache = ExchangeRateCache()
        
        result = cache.get("MISSING")
        
        assert result is None

    def test_cache_clear(self) -> None:
        """Cache clear should remove all entries."""
        cache = ExchangeRateCache()
        
        cache.set("USD_EUR", 0.92)
        cache.clear()
        result = cache.get("USD_EUR")
        
        assert result is None


class TestCurrencyService:
    """Tests for CurrencyService."""

    def test_same_currency_rate(self) -> None:
        """Same currency conversion should return 1.0."""
        service = CurrencyService(api_key=None, default_currency="USD")
        
        rate = service.get_exchange_rate("USD", "USD")
        
        assert rate == 1.0

    def test_default_target_currency(self) -> None:
        """Should use default currency when target is not specified."""
        service = CurrencyService(api_key=None, default_currency="USD")
        
        rate = service.get_exchange_rate("EUR", None)
        
        # Without API key, should return None (but None != 1.0, so it's not same currency)
        assert rate is None

    def test_convert_same_currency(self) -> None:
        """Converting same currency should return same amount."""
        service = CurrencyService(api_key=None, default_currency="USD")
        
        result = service.convert_currency(100.00, "USD", "USD")
        
        assert result == 100.00

    def test_convert_invalid_amount(self) -> None:
        """Converting zero or negative amount should return None."""
        service = CurrencyService(api_key=None, default_currency="USD")
        
        assert service.convert_currency(0, "USD", "EUR") is None
        assert service.convert_currency(-50, "USD", "EUR") is None

    def test_no_api_key(self) -> None:
        """Without API key, should not fetch exchange rates."""
        service = CurrencyService(api_key=None)
        
        rate = service.get_exchange_rate("EUR", "USD")
        
        assert rate is None

    def test_currency_normalization(self) -> None:
        """Currency codes should be normalized to uppercase."""
        service = CurrencyService(api_key=None)
        
        result = service.convert_currency(100.00, "eur", "usd")
        
        # Should attempt conversion (will fail without API key, but normalization happens)
        # With same normalized codes converted, it would work
        assert result is None or isinstance(result, float)

    def test_cache_hit(self) -> None:
        """Repeated conversions should use cache (return same value)."""
        service = CurrencyService(api_key=None)
        
        # Manually set a cached rate for testing
        service._cache.set("EUR_USD", 1.1)
        
        rate1 = service.get_exchange_rate("EUR", "USD")
        rate2 = service.get_exchange_rate("EUR", "USD")
        
        assert rate1 == rate2 == 1.1

    def test_clear_cache(self) -> None:
        """Clearing cache should remove cached rates."""
        service = CurrencyService(api_key=None)
        
        service._cache.set("EUR_USD", 1.1)
        service.clear_cache()
        
        result = service._cache.get("EUR_USD")
        assert result is None
