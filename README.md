# 🔌 local-mcp-server

A locally hosted **Model Context Protocol (MCP)** server that exposes tools and resources to AI assistants like Claude. This server enables seamless integration between large language models and your local data, services, or APIs.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🧠 Overview

`local-mcp-server` is a lightweight MCP-compliant server that allows AI models (such as Claude via Claude.ai or the Anthropic API) to interact with tools and data sources running on your local machine or private infrastructure.

Built on the [Model Context Protocol](https://modelcontextprotocol.io/) standard, it enables structured, tool-based communication between AI assistants and backend services — without exposing sensitive data to the cloud.

---

## ✨ Features

- ✅ Fully MCP-compliant server implementation
- 🔧 Exposes custom tools callable by AI assistants
- 💾 Connects to a local database for expense/data tracking
- 🔒 Runs entirely on your local machine — no external data exposure
- ⚡ Fast and lightweight — minimal dependencies
- 🔄 Easy to extend with new tools and resources

---

## 🛠 Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version |
|-------------|---------|
| Node.js | `>= 18.x` |
| npm | `>= 9.x` |
| Python *(optional)* | `>= 3.9` |

---

## 📦 Installation

**1. Clone the repository:**

```bash
git clone https://github.com/anamika-1520/local-mcp-server.git
cd local-mcp-server
```

**2. Install dependencies:**

```bash
npm install
```

**3. Set up the database (if applicable):**

```bash
npm run db:setup
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory by copying the example:

```bash
cp .env.example .env
```

Edit `.env` to configure your environment:

```env
# Server Configuration
PORT=3000
HOST=localhost

# Database
DB_PATH=./data/expenses.db

# MCP Settings
MCP_SERVER_NAME=local-mcp-server
MCP_SERVER_VERSION=1.0.0
```

---

## 🚀 Usage

**Start the server:**

```bash
npm start
```

**Start in development mode (with auto-reload):**

```bash
npm run dev
```

The server will start and listen for MCP connections. You can connect it to Claude.ai or any MCP-compatible client by registering the server URL:

```
http://localhost:3000/mcp/v1
```

### Connecting to Claude.ai

1. Go to **Claude.ai → Settings → Integrations**
2. Click **Add MCP Server**
3. Enter your server URL: `http://localhost:3000/mcp/v1`
4. Save and start using your tools in conversations

---

## 🧰 Available Tools

The server currently exposes the following tools to connected AI assistants:

### `add_expense`
Add a new expense entry to the local database.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | `number` | ✅ | Expense amount |
| `category` | `string` | ✅ | Category (e.g., Food, Transport) |
| `date` | `string` | ✅ | Date in `YYYY-MM-DD` format |
| `note` | `string` | ❌ | Optional note or description |
| `subcategory` | `string` | ❌ | Optional subcategory |

---

### `list_expenses`
Retrieve all expense entries within a date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | `string` | ✅ | Start date (`YYYY-MM-DD`) |
| `end_date` | `string` | ✅ | End date (`YYYY-MM-DD`) |

---

### `summarize`
Get a category-wise summary of expenses within a date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | `string` | ✅ | Start date (`YYYY-MM-DD`) |
| `end_date` | `string` | ✅ | End date (`YYYY-MM-DD`) |
| `category` | `string` | ❌ | Filter by specific category |

---

## 🗂 Project Structure

```
local-mcp-server/
├── src/
│   ├── index.js          # Server entry point
│   ├── tools/            # MCP tool definitions
│   │   ├── addExpense.js
│   │   ├── listExpenses.js
│   │   └── summarize.js
│   ├── db/               # Database layer
│   │   ├── schema.js
│   │   └── queries.js
│   └── utils/            # Helper utilities
├── data/                 # Local SQLite database (auto-created)
├── .env.example          # Environment variable template
├── package.json
└── README.md
```

---

## 🧑‍💻 Development

### Running Tests

```bash
npm test
```

### Adding a New Tool

1. Create a new file under `src/tools/yourTool.js`
2. Define the tool schema and handler function
3. Register the tool in `src/index.js`

**Example tool definition:**

```javascript
export const yourTool = {
  name: "your_tool",
  description: "Description of what your tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "A parameter" }
    },
    required: ["param1"]
  },
  handler: async ({ param1 }) => {
    // Your logic here
    return { result: `Processed: ${param1}` };
  }
};
```

---

## 🐛 Troubleshooting

**Server won't start:**
- Ensure port `3000` is not in use: `lsof -i :3000`
- Check Node.js version: `node --version` (must be ≥ 18)

**Claude can't connect to the server:**
- Make sure the server is running before connecting
- Confirm the MCP URL is correct in Claude settings
- Check firewall rules if running on a remote machine

**Database errors:**
- Delete `data/expenses.db` and re-run `npm run db:setup` to reset
- Ensure the `data/` directory has write permissions

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please ensure your code follows the existing style and includes relevant tests.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Anamika**
- GitHub: [@anamika-1520](https://github.com/anamika-1520)

---

> 💡 **Tip:** For best results, run this server alongside Claude.ai to enable intelligent, tool-augmented AI conversations with your own local data.
