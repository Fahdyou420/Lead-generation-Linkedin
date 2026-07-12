# Hunter Auto Pro: Local Agentic OS Guide

> [!IMPORTANT]
> **Before you start:** Read the [REALITY_CHECK_GUIDE.md](./REALITY_CHECK_GUIDE.md) to understand the technical limitations and LinkedIn ban risks associated with this automation.

You have upgraded to the **Pro Stack** (MCP + Nous Portal + Obsidian + Gemini Fallback). This architecture removes reliance on static local hardware and provides extremely fast, smart cloud-local execution.

## 1. Cloud-Local Intelligence (Nous Research Portal & Gemini)
The agent uses highly advanced AI models for lead scoring and message generation without requiring local GPU/RAM resources:
1. **Primary Model (Nous Research Portal):** Fully OpenAI-compatible API. Uses `stepfun/step-3.7-flash:free` by default.
2. **Fallback Model (Google Gemini):** Used automatically as a fallback to ensure 100% uptime and bypass rate-limits.

Configure these in your `.env` file:
```env
NOUS_API_KEY=your_key_here
NOUS_MODEL=stepfun/step-3.7-flash:free
GEMINI_API_KEY=your_key_here
```

## 2. Desktop Orchestration (Hermes Agent CLI)
We have removed **n8n** to keep deployment lightweight and private. If you need desktop orchestration:
- Use [Hermes Agent CLI for Windows](https://github.com/nousresearch/hermes-agent) to trigger scraper commands and interact with files on your host.

## 3. Model Context Protocol (MCP)
We have added `mcp_server.py`. This allows any MCP-compatible client (like Claude Desktop or Hermes Agent) to **drive** the Hunter Agent.
To use with Claude Desktop:
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "hunter": {
      "command": "python",
      "args": ["C:/path/to/hunter_auto/mcp_server.py"]
    }
  }
}
```
Claude will now have native tools to "Scrape Leads" and "Get Dashboard Stats" directly in your chat interface.

## 4. Skills & Knowledge (Obsidian)
Your skills are now in markdown:
- Create folders in Obsidian and link them to the `hunter_auto/knowledge` folder.
- When you update a markdown file (e.g., `closing_tips.md`), the agent's MCP tool `read_skill_or_knowledge` will immediately reflect the new strategy.

## 5. Deployment
```bash
docker compose up -d --build
```
This boots the Python Agent and the Flask Dashboard instantly.
