# 💸 Expense Tracker MCP Server

A local **Model Context Protocol (MCP)** server built with [FastMCP](https://github.com/jlowin/fastmcp) that lets AI assistants like **Claude** manage your personal expenses — add entries, list them by date range, and get category-wise summaries — all stored in a local SQLite database.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Connecting to Claude](#connecting-to-claude)
- [Tools & Resources](#tools--resources)
- [Expense Categories](#expense-categories)
- [Database Schema](#database-schema)
- [Contributing](#contributing)

---

## 🧠 Overview

`expense-tracker-server` exposes three MCP tools and one MCP resource to any connected AI client. Claude (or any MCP-compatible assistant) can call these tools directly in conversation to log and query your expenses — no manual spreadsheet needed.

All data is stored locally in `expenses.db` (SQLite), and categories are managed via a simple `categories.json` file that you can edit without restarting the server.

---

## ✨ Features

- 🤖 **AI-native** — designed to be called by Claude via MCP
- 💾 **Local SQLite storage** — your data stays on your machine
- 📂 **20 expense categories** with subcategories (fully customizable via JSON)
- 🔧 **FastMCP-powered** — minimal boilerplate, clean tool definitions
- 🔄 **Live category reload** — edit `categories.json` without restarting
- 🐍 **Pure Python** — easy to read, extend, and modify

---

## 🗂 Project Structure

```
expense-tracker-server/
├── main.py             # FastMCP server — tools & resource definitions
├── expenses.db         # SQLite database (auto-created on first run)
├── categories.json     # Expense categories and subcategories
├── fastmcp.json        # FastMCP module config
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # Locked dependency versions (uv)
├── .python-version     # Python version pin
└── README.md
```

---

## 🛠 Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | `>= 3.14` |
| [uv](https://github.com/astral-sh/uv) | latest recommended |

> **Why uv?** This project uses `uv` for fast dependency management and virtual environment handling. You can also use plain `pip` if preferred.

---

## 📦 Installation

**1. Clone the repository:**

```bash
git clone https://github.com/anamika-1520/local-mcp-server.git
cd local-mcp-server
```

**2. Install dependencies using `uv`:**

```bash
uv sync
```

Or using `pip`:

```bash
pip install fastmcp>=3.2.2
```

> The `expenses.db` SQLite database is created automatically when the server starts for the first time.

---

## 🚀 Running the Server

```bash
uv run main.py
```

Or directly with Python:

```bash
python main.py
```

The server will start and listen for incoming MCP connections.

---

## 🔌 Connecting to Claude

### Claude.ai (Remote MCP)

If you expose this server via a tunnel (e.g., `ngrok` or `cloudflared`):

1. Go to **Claude.ai → Settings → Integrations**
2. Click **Add MCP Server**
3. Enter your server's public URL
4. Start using the tools in any conversation

### Claude Desktop (Local MCP)

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "expense-tracker": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "/path/to/expense-tracker-server"
    }
  }
}
```

---

## 🧰 Tools & Resources

### 🔧 Tool: `add_expense`

Add a new expense entry to the database.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | `string` | ✅ | Date in `YYYY-MM-DD` format |
| `amount` | `float` | ✅ | Expense amount |
| `category` | `string` | ✅ | Main category (e.g., `food`, `transport`) |
| `subcategory` | `string` | ❌ | Subcategory (e.g., `groceries`, `fuel`) |
| `note` | `string` | ❌ | Optional description or note |

**Example response:**
```json
{ "status": "ok", "id": 7 }
```

---

### 🔧 Tool: `list_expenses`

List all expense entries within an inclusive date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | `string` | ✅ | Start date (`YYYY-MM-DD`) |
| `end_date` | `string` | ✅ | End date (`YYYY-MM-DD`) |

**Example response:**
```json
[
  {
    "id": 1,
    "date": "2026-04-01",
    "amount": 500.0,
    "category": "food",
    "subcategory": "groceries",
    "note": "Weekly shop"
  }
]
```

---

### 🔧 Tool: `summarize`

Get a category-wise total of expenses within a date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | `string` | ✅ | Start date (`YYYY-MM-DD`) |
| `end_date` | `string` | ✅ | End date (`YYYY-MM-DD`) |
| `category` | `string` | ❌ | Filter to a single category |

**Example response:**
```json
[
  { "category": "food", "total_amount": 1850.0 },
  { "category": "transport", "total_amount": 640.0 }
]
```

---

### 📦 Resource: `expense://categories`

Returns the full list of categories and subcategories from `categories.json` as `application/json`.

This resource is **read fresh on every call**, so you can update `categories.json` at any time without restarting the server.

---

## 🏷 Expense Categories

The server supports **20 top-level categories**, each with subcategories:

| Category | Example Subcategories |
|---|---|
| `food` | groceries, dining_out, delivery_fees, snacks |
| `transport` | fuel, cab_ride_hailing, public_transport, tolls |
| `housing` | rent, repairs_service, furnishing |
| `utilities` | electricity, internet_broadband, mobile_phone |
| `health` | medicines, doctor_consultation, fitness_gym |
| `education` | books, courses, workshops, exam_fees |
| `entertainment` | movies_events, streaming_subscriptions, outing |
| `shopping` | clothing, electronics_gadgets, home_decor |
| `travel` | flights, hotels, train_bus, visa_passport |
| `investments` | mutual_funds, stocks, crypto, gold |
| `subscriptions` | saas_tools, cloud_ai, music_video |
| `personal_care` | salon_spa, grooming, cosmetics |
| `family_kids` | school_fees, toys_games, events_birthdays |
| `gifts_donations` | charity_donation, gifts_personal, festivals |
| `finance_fees` | bank_charges, interest, brokerage |
| `business` | hosting_domains, marketing_ads, contractor_payments |
| `home` | household_supplies, kitchenware, pest_control |
| `pet` | food, vet, grooming, supplies |
| `taxes` | income_tax, gst, professional_tax |
| `misc` | uncategorized, other |

> You can freely add, remove, or rename categories by editing `categories.json`. No server restart needed.

---

## 🗄 Database Schema

The SQLite database (`expenses.db`) uses a single table:

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,
    amount      REAL    NOT NULL,
    category    TEXT    NOT NULL,
    subcategory TEXT    DEFAULT '',
    note        TEXT    DEFAULT ''
);
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👤 Author

**Anamika**
- GitHub: [@anamika-1520](https://github.com/anamika-1520)

---

> Built with [FastMCP](https://github.com/jlowin/fastmcp) · Powered by SQLite · Designed for Claude
