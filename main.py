from fastmcp import FastMCP
import os
import sqlite3
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY") or "USD"


# Exchange rate cache (API response caching)
_exchange_rate_cache = {}

mcp = FastMCP("ExpenseTracker", auth=None)


def get_exchange_rate(from_currency, to_currency=DEFAULT_CURRENCY):
    '''Fetch exchange rate from exchangerate-api.com. Returns float or None on error.'''
    if from_currency == to_currency:
        return 1.0
    
    cache_key = f"{from_currency}_{to_currency}"
    if cache_key in _exchange_rate_cache:
        return _exchange_rate_cache[cache_key]
    
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        logger.warning("EXCHANGE_RATE_API_KEY not set. Cannot fetch exchange rates.")
        return None
    
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get("result") == "success":
            rate = data.get("conversion_rate")
            if rate:
                _exchange_rate_cache[cache_key] = rate
                return rate
        else:
            logger.warning(f"API error: {data.get('error-type', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch exchange rate: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse exchange rate response: {e}")
        return None

def convert_currency(amount, source_currency, target_currency=DEFAULT_CURRENCY):
    '''Convert amount from source currency to target currency. Returns float or None on error.'''
    if not amount or amount <= 0:
        return None
    
    if source_currency.upper() == target_currency.upper():
        return amount
    
    rate = get_exchange_rate(source_currency.upper(), target_currency.upper())
    if rate is None:
        logger.warning(f"Cannot convert {source_currency} to {target_currency}, rate not available")
        return None
    
    return round(amount * rate, 2)

def init_db():
    '''Initialize database and run migrations.'''
    with sqlite3.connect(DB_PATH) as c:
        # Create table if not exists
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT '',
                usd_amount REAL DEFAULT NULL,
                original_currency TEXT DEFAULT NULL
            )
        """)
        
        c.commit()

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note="", currency=DEFAULT_CURRENCY):
    '''Add a new expense entry to the database with optional currency conversion to USD.
    
    Args:
        date: Expense date (YYYY-MM-DD format)
        amount: Expense amount in the original currency
        category: Expense category
        subcategory: Expense subcategory (optional)
        note: Expense description (optional)
        currency: Currency code (e.g., "USD", "EUR", "GBP"). If not provided, uses default from config.json
    
    Returns:
        Dictionary with status, id, original_amount, original_currency, and usd_amount
    '''
    try:
        # Get currency from parameter or config
        if not currency:
            currency = DEFAULT_CURRENCY
        
        currency = currency.upper()
        
        # Validate amount
        if not isinstance(amount, (int, float)) or amount <= 0:
            return {"status": "error", "message": "Amount must be a positive number"}
        
        # Convert to USD
        if currency != 'USD':
            usd_amount = convert_currency(amount, currency, 'USD')
        else:
            usd_amount = amount
        
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute(
                """INSERT INTO expenses(date, amount, category, subcategory, note, original_currency, usd_amount) 
                   VALUES (?,?,?,?,?,?,?)""",
                (date, amount, category, subcategory, note, currency, usd_amount)
            )
            return {
                "status": "ok",
                "id": cur.lastrowid,
                "original_amount": amount,
                "original_currency": currency,
                "usd_amount": usd_amount
            }
    except Exception as e:
        logger.error(f"Error adding expense: {e}")
        return {"status": "error", "message": str(e)}
    
@mcp.tool()
def list_expenses(start_date, end_date):
    '''List expense entries within an inclusive date range with currency information.'''
    try:
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute(
                """
                SELECT id, date, amount, category, subcategory, note, original_currency, usd_amount
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY id ASC
                """,
                (start_date, end_date)
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error listing expenses: {e}")
        return []

@mcp.tool()
def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.
    
    Args:
        start_date: Start date (inclusive, YYYY-MM-DD format)
        end_date: End date (inclusive, YYYY-MM-DD format)
        category: Optional filter by category
    
    Returns:
        List of dictionaries with category and total_amount (or total_usd_amount if converted)
    '''
    try:
        with sqlite3.connect(DB_PATH) as c:
            query = (
                    """
                    SELECT category, SUM(amount) AS total_amount, original_currency
                    FROM expenses
                    WHERE date BETWEEN ? AND ?
                    """
            )

            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY category ASC"

            cur = c.execute(query, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error summarizing expenses: {e}")
        return []

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()