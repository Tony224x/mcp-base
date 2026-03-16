# Claude API + MCP Bridge

Bridges MCP tool discovery into the Anthropic Claude API's native `tool_use` feature, implementing a full agent loop.

## Architecture

```
User Message
    |
    v
Claude API (with MCP tools as Claude tools)
    |
    v  (stop_reason == "tool_use")
MCP Server (call_tool)
    |
    v  (tool results)
Claude API (continue conversation)
    |
    v  (stop_reason == "end_turn")
Final Answer
```

## Key Concepts

### Tool Schema Conversion

MCP and the Claude API use slightly different tool formats. The `mcp_tool_to_claude_tool()` function converts between them:

```python
# MCP tool has: .name, .description, .inputSchema
# Claude API wants: {"name": ..., "description": ..., "input_schema": ...}
def mcp_tool_to_claude_tool(tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema,
    }
```

The schemas are compatible because both use JSON Schema for input definitions.

### Agent Loop

The agent loop follows this pattern:

1. Send user message + tool definitions to Claude
2. If `response.stop_reason == "tool_use"`:
   - Extract tool call(s) from response content blocks
   - Call the MCP server with `session.call_tool(name, args)`
   - Send tool results back to Claude as `tool_result` messages
3. Repeat until Claude gives a text response (`stop_reason == "end_turn"`)

### Multi-Tool Calls

Claude can request multiple tool calls in a single response. The loop processes all of them and sends all results back together.

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python clients/claude_api/client.py
```

## Tests

The tests validate tool conversion and MCP discovery without requiring an API key:

```bash
uv run pytest clients/claude_api/ -v
```
