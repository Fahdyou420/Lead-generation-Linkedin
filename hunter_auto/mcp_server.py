import sys
import os
from mcp.server.fastmcp import FastMCP
from scheduler.agent import HunterAgent
from database.sheets_client import SheetsClient
from outreach.telegram_notifier import TelegramNotifier

# Create the MCP server
mcp = FastMCP("HunterAuto-Pro")

# Persistent Agent context
agent = HunterAgent()
db = SheetsClient()
tg = TelegramNotifier()

@mcp.tool()
def scrape_now() -> str:
    """Trigger an immediate scrape and enrichment cycle."""
    try:
        agent.scrape_job()
        return "Scrape job completed and added to Google Sheets."
    except Exception as e:
        return f"Scrape failed: {str(e)}"

@mcp.tool()
def get_dashboard_summary() -> str:
    """Retrieve the latest stats and recent leads from the database."""
    try:
        stats = db.get_stats()
        return f"Current Stats: {stats}"
    except Exception as e:
        return f"Failed to get stats: {str(e)}"

@mcp.tool()
def notify_user(message: str) -> str:
    """Send a custom notification to the Telegram channel."""
    try:
        tg.send_msg(message)
        return "Telegram notification sent."
    except Exception as e:
        return f"Failed to send Telegram: {str(e)}"

@mcp.tool()
def read_skill_or_knowledge(topic: str) -> str:
    """Read context or 'Skills' from the markdown knowledge base (Obsidian)."""
    kb_path = os.path.join("knowledge", f"{topic}.md")
    if os.path.exists(kb_path):
        with open(kb_path, "r") as f:
            return f.read()
    return f"Topic '{topic}' not found in knowledge base."

if __name__ == "__main__":
    mcp.run()
