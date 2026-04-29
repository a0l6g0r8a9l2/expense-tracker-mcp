# Multi-Currency Support Setup Guide

## 📋 Overview

The Expense Tracker MCP now supports multi-currency expense tracking with automatic USD conversion using **exchangerate-api.com**.

### What's New

- ✅ Store expenses in any currency (USD, EUR, GBP, JPY, etc.)
- ✅ Automatic conversion to USD using live exchange rates
- ✅ Graceful error handling if API is unavailable
- ✅ Configurable default currency
- ✅ USD amounts are cached per session for performance

---

## 🔧 Setup

### Step 1: Get an API Key

1. Visit [exchangerate-api.com](https://www.exchangerate-api.com/)
2. Sign up for a free account (1,500 requests/month)
3. Copy your API key from the dashboard

### Step 2: Set Environment Variable

#### On Linux/macOS:
```bash
export EXCHANGE_RATE_API_KEY="your_api_key_here"
```

#### On Windows (PowerShell):
```powershell
$env:EXCHANGE_RATE_API_KEY = "your_api_key_here"
```

#### Permanent Setup (Linux/macOS):
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export EXCHANGE_RATE_API_KEY="your_api_key_here"
```

#### Using .env File (Optional):
Create `.env` file in project root:
```env
EXCHANGE_RATE_API_KEY=your_api_key_here
```

Then install python-dotenv and load it in main.py (optional enhancement).

### Step 3: Verify Installation

```bash
# Reinstall dependencies (if needed)
pip install -r requirements.txt
# or
pip install fastmcp requests

# Run the test suite
python3 test_currency_conversion.py
```

---

## 📖 Usage Examples

### Example 1: Add Expense in EUR

```python
from main import add_expense

result = add_expense(
    date="2024-01-15",
    amount=50,
    category="food",
    subcategory="groceries",
    note="Supermarket in Paris",
    currency="EUR"
)

print(result)
# Output:
# {
#   "status": "ok",
#   "id": 1,
#   "original_amount": 50,
#   "original_currency": "EUR",
#   "usd_amount": 54.32  # Converted using live rate
# }
```

### Example 2: Add Expense Without Currency (Uses Default)

```python
result = add_expense(
    date="2024-01-15",
    amount=100,
    category="food",
    subcategory="groceries"
)

# Uses default currency from config.json (usually "USD")
print(result["original_currency"])  # "USD"
```

### Example 3: List Expenses with Currency Info

```python
from main import list_expenses

expenses = list_expenses("2024-01-01", "2024-12-31")

for exp in expenses:
    print(f"{exp['date']}: {exp['amount']} {exp['original_currency']} -> ${exp['usd_amount']}")
    
# Output:
# 2024-01-15: 50 EUR -> $54.32
# 2024-01-16: 100 USD -> $100.00
# 2024-01-17: 3000 JPY -> $20.50
```

### Example 4: Summarize by Category (Original Currency)

```python
from main import summarize

result = summarize("2024-01-01", "2024-12-31")

for row in result:
    print(f"{row['category']}: {row['total_amount']} {row['original_currency']}")
    
# Output:
# food: 3100 USD
# transport: 50 EUR
# housing: 75 GBP
```

### Example 5: Summarize by Category (Converted to USD)

```python
result = summarize("2024-01-01", "2024-12-31", convert_to_usd_flag=True)

for row in result:
    print(f"{row['category']}: ${row['total_usd_amount']}")
    
# Output:
# food: $3100.00
# transport: $54.32
# housing: $81.50
```

---

## ⚙️ Configuration

### config.json

Edit `config.json` to change the default currency:

```json
{
  "default_currency": "EUR"
}
```

Now all expenses without a currency parameter will be in EUR by default.

---

## 🔄 Supported Currencies

The API supports all major currencies. Here are some examples:

| Code | Currency |
|------|----------|
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| JPY | Japanese Yen |
| AUD | Australian Dollar |
| CAD | Canadian Dollar |
| CHF | Swiss Franc |
| CNY | Chinese Yuan |
| INR | Indian Rupee |
| RUB | Russian Ruble |

[Full list of supported currencies](https://www.exchangerate-api.com/docs/supported-currencies)

---

## ⚠️ Error Handling

### When API Key is Not Set

If `EXCHANGE_RATE_API_KEY` is not set:
- ✅ Expenses are still saved normally
- ⚠️ `usd_amount` will be `None`
- 📝 Warning message is logged

This allows the system to degrade gracefully.

### When API is Unavailable

If exchangerate-api.com is down or unreachable:
- ✅ Expenses are still saved normally
- ⚠️ `usd_amount` will be `None`
- 📝 Warning message is logged

### Invalid Currency Code

If an invalid currency code is used (e.g., "XYZ"):
- ❌ Expense is still saved
- ⚠️ `usd_amount` will be `None`
- 📝 Error message is logged

---

## 📊 Database Schema

New fields added to `expenses` table:

| Field | Type | Description |
|-------|------|-------------|
| `original_currency` | TEXT | Currency code (e.g., "USD", "EUR") |
| `usd_amount` | REAL | Amount converted to USD (or NULL if conversion failed) |

All existing expenses are migrated with:
- `original_currency = "USD"` (safe assumption)
- `usd_amount = NULL` (until conversion happens)

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_currency_conversion.py
```

This will:
- ✓ Verify database schema
- ✓ Test exchange rate fetching (if API key is set)
- ✓ Add sample expenses in multiple currencies
- ✓ Test list and summarize functions
- ✓ Test error handling

---

## 🚀 Performance Tips

1. **Exchange rates are cached per session** — fetching the same rate twice doesn't make 2 API calls
2. **Free tier of exchangerate-api has 1,500 requests/month** — average 50 requests/day
3. **One API call per unique currency conversion** — converting 100 EUR expenses = 1 API call

---

## 🐛 Troubleshooting

### Problem: "EXCHANGE_RATE_API_KEY not set" warning

**Solution:** Set the environment variable
```bash
export EXCHANGE_RATE_API_KEY="your_key"
```

### Problem: API returns 401 (Unauthorized)

**Solution:** Check that your API key is correct. Get a new one from https://www.exchangerate-api.com/

### Problem: usd_amount is None for valid currencies

**Solution:** 
1. Check that API key is set correctly
2. Check your API request quota (max 1,500/month on free tier)
3. Try running test again after 1 hour

### Problem: Database migration failed

**Solution:** Delete `expenses.db` and let it reinitialize:
```bash
rm expenses.db
python3 -c "from main import init_db; init_db()"
```

---

## 📚 Related Links

- [exchangerate-api.com Documentation](https://www.exchangerate-api.com/docs/python-currency-api)
- [ISO 4217 Currency Codes](https://www.iso.org/iso-4217-currency-codes.html)
- [MCP (Model Context Protocol) Spec](https://modelcontextprotocol.io/)

---

## 💡 Future Enhancements (Not Yet Implemented)

- [ ] Persistent cache of exchange rates (database table)
- [ ] Historical exchange rates for past dates
- [ ] Cryptocurrency support
- [ ] Budget alerts based on USD amounts
- [ ] Exchange rate volatility notifications
- [ ] Custom API provider support

