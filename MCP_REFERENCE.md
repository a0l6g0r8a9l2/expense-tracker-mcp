# MCP Tool Reference - Multi-Currency Support

## Tools Available

### 1. `add_expense`
Add a new expense entry with optional currency conversion.

**Parameters:**
- `date` (string, required): Expense date in YYYY-MM-DD format
- `amount` (number, required): Expense amount
- `category` (string, required): Expense category
- `subcategory` (string, optional): Subcategory name
- `note` (string, optional): Description of expense
- `currency` (string, optional): Currency code (default: from config.json, usually "USD")

**Returns:**
```json
{
  "status": "ok",
  "id": 123,
  "original_amount": 50.0,
  "original_currency": "EUR",
  "usd_amount": 54.32
}
```

**Example:**
```
Claude: Add an expense of 50 EUR for groceries on January 15th.

Tool Call:
add_expense(
  date="2024-01-15",
  amount=50,
  category="food",
  subcategory="groceries",
  currency="EUR"
)

Response:
{
  "status": "ok",
  "id": 42,
  "original_amount": 50,
  "original_currency": "EUR",
  "usd_amount": 54.32
}
```

---

### 2. `list_expenses`
List all expenses within a date range with currency information.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format (inclusive)
- `end_date` (string, required): End date in YYYY-MM-DD format (inclusive)

**Returns:**
```json
[
  {
    "id": 1,
    "date": "2024-01-15",
    "amount": 50.0,
    "category": "food",
    "subcategory": "groceries",
    "note": "Supermarket",
    "original_currency": "EUR",
    "usd_amount": 54.32
  },
  {
    "id": 2,
    "date": "2024-01-16",
    "amount": 100.0,
    "category": "food",
    "subcategory": "dining_out",
    "note": "Restaurant",
    "original_currency": "USD",
    "usd_amount": 100.0
  }
]
```

**Example:**
```
Claude: Show me all expenses from January 2024.

Tool Call:
list_expenses(
  start_date="2024-01-01",
  end_date="2024-01-31"
)

Response: [array of 15 expenses with currency info]
```

---

### 3. `summarize`
Summarize expenses by category with optional USD conversion.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format (inclusive)
- `end_date` (string, required): End date in YYYY-MM-DD format (inclusive)
- `category` (string, optional): Filter by specific category
- `convert_to_usd_flag` (boolean, optional): If true, return amounts in USD. Default: false

**Returns (convert_to_usd_flag=false):**
```json
[
  {
    "category": "food",
    "total_amount": 3100.0,
    "original_currency": "USD"
  },
  {
    "category": "transport",
    "total_amount": 50.0,
    "original_currency": "EUR"
  }
]
```

**Returns (convert_to_usd_flag=true):**
```json
[
  {
    "category": "food",
    "total_usd_amount": 3100.0
  },
  {
    "category": "transport",
    "total_usd_amount": 54.32
  }
]
```

**Examples:**

```
Claude: What did I spend on food in January?

Tool Call:
summarize(
  start_date="2024-01-01",
  end_date="2024-01-31",
  category="food"
)

Response:
[
  {
    "category": "food",
    "total_amount": 3100.0,
    "original_currency": "USD"
  }
]
```

```
Claude: What were my total spending by category in January, converted to USD?

Tool Call:
summarize(
  start_date="2024-01-01",
  end_date="2024-01-31",
  convert_to_usd_flag=true
)

Response:
[
  {"category": "food", "total_usd_amount": 3200.50},
  {"category": "transport", "total_usd_amount": 145.32},
  {"category": "housing", "total_usd_amount": 1000.00}
]
```

---

## Resource: Categories

### `expense://categories`

Get available expense categories as JSON.

**MIME Type:** `application/json`

**Returns:**
```json
{
  "food": [
    "groceries",
    "fruits_vegetables",
    "dairy_bakery",
    "dining_out",
    "coffee_tea",
    "snacks",
    "delivery_fees",
    "other"
  ],
  "transport": [
    "fuel",
    "public_transport",
    "cab_ride_hailing",
    "parking",
    "tolls",
    "vehicle_service",
    "other"
  ],
  "housing": [
    "rent",
    "maintenance_hoa",
    "property_tax",
    "repairs_service",
    "cleaning",
    "furnishing",
    "other"
  ],
  ...
}
```

---

## Common Use Cases

### 1. Track International Travel Expenses

```
Claude: I'm traveling in Europe. Add my expenses:
- €50 for food in Paris
- £30 for transport in London
- ¥3000 for food in Tokyo

Tool Calls:
1. add_expense(date="2024-03-15", amount=50, category="food", currency="EUR", note="Paris dinner")
2. add_expense(date="2024-03-16", amount=30, category="transport", currency="GBP", note="London taxi")
3. add_expense(date="2024-03-17", amount=3000, category="food", currency="JPY", note="Tokyo restaurant")
```

### 2. Get Total Spending in USD

```
Claude: What's my total spending in USD for March?

Tool Call:
summarize(
  start_date="2024-03-01",
  end_date="2024-03-31",
  convert_to_usd_flag=true
)
```

### 3. Compare Spending by Currency

```
Claude: How much did I spend in each currency in Q1?

Tool Call:
summarize(
  start_date="2024-01-01",
  end_date="2024-03-31"
)
```

---

## Important Notes

⚠️ **Requirements:**
- API key from exchangerate-api.com set in `EXCHANGE_RATE_API_KEY` environment variable
- See [CURRENCY_SETUP.md](CURRENCY_SETUP.md) for setup instructions

✅ **Graceful Degradation:**
- If API key is not set, expenses are saved but USD conversion won't work
- `usd_amount` will be `None` if conversion fails
- All operations continue to work normally

🔄 **Exchange Rates:**
- Fetched from exchangerate-api.com in real-time
- Cached per session for performance
- Uses `EXCHANGE_RATE_API_KEY` for authentication

💾 **Database:**
- All amounts stored with original currency
- USD amounts stored for easy reporting
- Backward compatible with pre-currency data (new fields default to NULL)

---

## Example MCP Prompt

Here's an example of how Claude would use these tools:

```
User: I spent €100 on food in Paris on Jan 15, then $50 in NYC on Jan 16. 
      Show me my spending summary for January in USD.

Claude: I'll help you track those international expenses and summarize them in USD.

Step 1: Add the Paris expense
[Tool Call: add_expense(date="2024-01-15", amount=100, category="food", currency="EUR", note="Food in Paris")]
✓ Saved: 100 EUR → ~$108.50 USD

Step 2: Add the NYC expense
[Tool Call: add_expense(date="2024-01-16", amount=50, category="food", currency="USD", note="Food in NYC")]
✓ Saved: 50 USD → $50.00 USD

Step 3: Summarize food spending in USD
[Tool Call: summarize(start_date="2024-01-01", end_date="2024-01-31", category="food", convert_to_usd_flag=true)]

Summary of food spending in January (USD):
- Total: $158.50 USD
  - Paris: ~$108.50 EUR
  - NYC: $50.00 USD

Done! Your international food expenses have been tracked and converted to USD.
```

---

## API Limits

**Free Plan (exchangerate-api.com):**
- 1,500 requests per month (~50 per day)
- One conversion per unique currency pair per session (cached)
- Response time: ~100-200ms per API call

**Tips to stay within limits:**
- Exchange rates are cached, so converting the same currencies multiple times doesn't use extra requests
- USD is the most common target, usually requires only 1 API call per unique source currency
- Batch expenses by currency to minimize API calls

