"""ExpenseTracker MCP Server - Main entry point."""

from fastmcp import FastMCP

from app.logger import configure_logging
from app.mcp_tools import register_tools

# Configure logging
configure_logging()

# Initialize FastMCP server
mcp = FastMCP("ExpenseTracker", auth=None)

# Register all tools and resources
register_tools(mcp)

if __name__ == "__main__":
    mcp.run()