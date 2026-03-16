# MCP Clients

This directory contains three client modules that demonstrate different ways to consume MCP servers. Each module builds on the previous one, from low-level SDK usage to full agent frameworks.

## Modules

### 1. `raw_client/` — MCP Client SDK Basics

Connect directly to an MCP server using the Python SDK. Demonstrates:
- `StdioServerParameters` for configuring the server process
- `stdio_client` for establishing the stdio transport
- `ClientSession` for the MCP protocol handshake
- Discovery: listing tools, resources, and prompts
- Calling tools and reading results

**Run:** `uv run python clients/raw_client/client.py`

### 2. `claude_api/` — Claude API + MCP Bridge

Bridge MCP tools into the Anthropic Claude API's native `tool_use` feature. Demonstrates:
- Converting MCP tool schemas to Claude API tool format
- Sending messages with tools to Claude
- Handling `tool_use` stop reasons
- Implementing a multi-turn agent loop (user → Claude → tool → Claude → ...)

**Run:** `ANTHROPIC_API_KEY=sk-... uv run python clients/claude_api/client.py`

### 3. `langchain_agent/` — LangChain ReAct Agent

Use `langchain-mcp-adapters` to load MCP tools as LangChain tools, then build a ReAct agent with LangGraph. Demonstrates:
- `load_mcp_tools()` for automatic MCP → LangChain conversion
- `create_react_agent()` for a reasoning + acting agent
- End-to-end query → reasoning → tool call → answer flow

**Run:** `ANTHROPIC_API_KEY=sk-... uv run python clients/langchain_agent/client.py`

## Testing

All clients have tests that validate tool discovery and basic functionality without requiring an API key:

```bash
uv run pytest clients/ -v
```

## Dependencies

These clients use optional dependency groups defined in `pyproject.toml`:

```bash
uv sync --all-extras  # Install everything
# Or selectively:
uv sync --extra anthropic   # For claude_api/
uv sync --extra langchain   # For langchain_agent/
```
