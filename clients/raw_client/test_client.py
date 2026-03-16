"""Tests for the raw MCP client — validates discovery and tool calls."""

from shared.testing import mcp_client_for


async def test_raw_client_discovers_tools():
    async with mcp_client_for("tutorials/01_hello_mcp/server.py") as client:
        tools = await client.list_tools()
        assert any(t.name == "echo" for t in tools.tools)


async def test_raw_client_calls_tool():
    async with mcp_client_for("tutorials/01_hello_mcp/server.py") as client:
        result = await client.call_tool("echo", {"message": "test"})
        assert result.content[0].text == "test"
