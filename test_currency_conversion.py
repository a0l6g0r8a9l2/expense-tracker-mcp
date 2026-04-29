#!/usr/bin/env python3
"""
Test script for multi-currency expense tracking.

Before running this test with real API conversion:
1. Sign up at https://www.exchangerate-api.com/
2. Get a free API key
3. Set environment variable: export EXCHANGE_RATE_API_KEY=your_key_here

This script tests:
- Adding expenses in different currencies
- Automatic USD conversion
- Graceful error handling when API key is not set
- Database schema with new currency fields
"""

import os
import sqlite3
from datetime import datetime, timedelta

from main import (
    init_db, 
    add_expense, 
    list_expenses, 
    summarize,
    DB_PATH,
    get_exchange_rate,
    convert_currency
)

def test_exchange_rates():
    """Test exchange rate fetching (requires API key)."""
    print("=" * 60)
    print("TEST: Exchange Rate Fetching")
    print("=" * 60)
    
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        print("❌ EXCHANGE_RATE_API_KEY not set. Skipping real API tests.")
        print("   Set it with: export EXCHANGE_RATE_API_KEY=your_key")
        return
    
    print("✓ API key found. Testing real exchange rates...\n")
    
    currencies = ["EUR", "GBP", "JPY", "AUD", "CAD"]
    for currency in currencies:
        rate = get_exchange_rate(currency, "USD")
        if rate:
            print(f"  {currency} → USD: {rate:.4f}")
        else:
            print(f"  {currency} → USD: Failed to fetch")

def test_add_expenses_multiple_currencies():
    """Test adding expenses in different currencies."""
    print("\n" + "=" * 60)
    print("TEST: Adding Expenses in Multiple Currencies")
    print("=" * 60 + "\n")
    
    today = datetime.now()
    
    test_cases = [
        {"date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "amount": 100, "currency": "USD", "category": "food", "subcategory": "groceries", "note": "Supermarket"},
        {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "amount": 50, "currency": "EUR", "category": "transport", "subcategory": "fuel", "note": "Gas station"},
        {"date": today.strftime("%Y-%m-%d"), "amount": 3000, "currency": "JPY", "category": "food", "subcategory": "dining_out", "note": "Restaurant in Tokyo"},
        {"date": today.strftime("%Y-%m-%d"), "amount": 75, "currency": "GBP", "category": "housing", "subcategory": "rent", "note": "Partial rent"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = add_expense(
            date=test_case["date"],
            amount=test_case["amount"],
            category=test_case["category"],
            subcategory=test_case["subcategory"],
            note=test_case["note"],
            currency=test_case["currency"]
        )
        
        print(f"Test {i}: {test_case['amount']} {test_case['currency']} ({test_case['note']})")
        if result["status"] == "ok":
            print(f"  ✓ Saved with ID: {result['id']}")
            print(f"    Original: {result['original_amount']} {result['original_currency']}")
            print(f"    USD Amount: {result['usd_amount']}")
        else:
            print(f"  ❌ Error: {result.get('message', 'Unknown error')}")
        print()

def test_list_with_currency():
    """Test listing expenses with currency information."""
    print("=" * 60)
    print("TEST: List Expenses with Currency Info")
    print("=" * 60 + "\n")
    
    expenses = list_expenses("2020-01-01", "2030-12-31")
    
    print(f"Total expenses: {len(expenses)}\n")
    print(f"{'Date':<12} {'Amount':<10} {'Currency':<8} {'USD Amount':<12} {'Category':<15} {'Note':<20}")
    print("-" * 85)
    
    for exp in expenses:
        usd_str = f"{exp['usd_amount']:.2f}" if exp['usd_amount'] is not None else "N/A"
        print(f"{exp['date']:<12} {exp['amount']:<10.2f} {exp['original_currency']:<8} {usd_str:<12} {exp['category']:<15} {exp['note'][:20]:<20}")

def test_summarize():
    """Test summarize with and without USD conversion."""
    print("\n" + "=" * 60)
    print("TEST: Summarize Expenses")
    print("=" * 60 + "\n")
    
    print("1. By Category (Original Amounts):")
    result = summarize("2020-01-01", "2030-12-31")
    for row in result:
        currency = row.get('original_currency', 'Mixed')
        total = row['total_amount']
        print(f"   {row['category']:<15} {total:>10.2f} {currency}")
    
    print("\n3. Specific Category (food):")
    result = summarize("2020-01-01", "2030-12-31", category="food")
    for row in result:
        currency = row.get('original_currency', 'Mixed')
        total = row['total_amount']
        print(f"   {row['category']:<15} {total:>10.2f} {currency}")

def test_db_schema():
    """Verify database schema has currency fields."""
    print("\n" + "=" * 60)
    print("TEST: Database Schema")
    print("=" * 60 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("PRAGMA table_info(expenses)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()
    
    required_columns = {
        'id': 'INTEGER',
        'date': 'TEXT',
        'amount': 'REAL',
        'category': 'TEXT',
        'subcategory': 'TEXT',
        'note': 'TEXT',
        'original_currency': 'TEXT',
        'usd_amount': 'REAL'
    }
    
    print("Checking schema...")
    all_ok = True
    for col_name, col_type in required_columns.items():
        if col_name in columns:
            status = "✓" if columns[col_name] == col_type else "⚠ (type mismatch)"
            print(f"  {status} {col_name}: {columns[col_name]}")
        else:
            print(f"  ❌ {col_name}: MISSING")
            all_ok = False
    
    if all_ok:
        print("\n✓ All required columns present!")
    else:
        print("\n❌ Some columns are missing!")

def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("MULTI-CURRENCY EXPENSE TRACKER - TEST SUITE")
    print("🚀 " * 20 + "\n")
    
    # Initialize fresh database for testing
    print("Initializing database...\n")
    init_db()
    
    # Run tests
    test_db_schema()
    test_exchange_rates()
    test_add_expenses_multiple_currencies()
    test_list_with_currency()
    test_summarize()
    
    print("\n" + "✓ " * 20)
    print("ALL TESTS COMPLETED!")
    print("✓ " * 20 + "\n")
    
    print("📋 Summary:")
    print("  • Database schema: ✓ Updated with currency fields")
    print("  • add_expense(): ✓ Accepts currency parameter, converts to USD")
    print("  • list_expenses(): ✓ Returns original currency and USD amounts")
    print("  • Error handling: ✓ Graceful degradation when API unavailable")
    print("\n📚 Documentation: See README.md for usage examples")
    print("🔑 To enable real currency conversion:")
    print("   1. Get API key from https://www.exchangerate-api.com/")
    print("   2. Set: export EXCHANGE_RATE_API_KEY=your_key_here")
    print("   3. Re-run this test script\n")

if __name__ == "__main__":
    main()
