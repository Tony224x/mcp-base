"""Tests for the Claude API client — validates tool conversion and discovery."""

from unittest.mock import MagicMock

from clients.claude_api.client import mcp_tool_to_claude_tool
from shared.testing import mcp_client_for


def test_mcp_tool_to_claude_tool():
    """Test converting MCP tool format to Claude API format."""
    mock_tool = MagicMock()
    mock_tool.name = "echo"
    mock_tool.description = "Echo a message"
    mock_tool.inputSchema = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }

    result = mcp_tool_to_claude_tool(mock_tool)
    assert result["name"] == "echo"
    assert result["description"] == "Echo a message"
    assert result["input_schema"]["properties"]["message"]["type"] == "string"


async def test_tool_discovery():
    """Test that we can discover tools from a server."""
    async with mcp_client_for("tutorials/02_tools_deep_dive/server.py") as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools.tools]
        assert "add" in tool_names
        assert "calculate_bmi" in tool_names
