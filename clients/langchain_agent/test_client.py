"""Tests for the LangChain agent — validates MCP tool loading without an API key."""

from langchain_mcp_adapters.tools import load_mcp_tools

from shared.testing import mcp_client_for


async def test_load_mcp_tools():
    """Test that MCP tools can be loaded as LangChain tools."""
    async with mcp_client_for("tutorials/02_tools_deep_dive/server.py") as client:
        tools = await load_mcp_tools(client)
        tool_names = [t.name for t in tools]
        assert "add" in tool_names
        assert len(tools) >= 4


async def test_tool_has_description():
    """Test that loaded tools preserve their descriptions."""
    async with mcp_client_for("tutorials/02_tools_deep_dive/server.py") as client:
        tools = await load_mcp_tools(client)
        add_tool = next(t for t in tools if t.name == "add")
        assert add_tool.description
