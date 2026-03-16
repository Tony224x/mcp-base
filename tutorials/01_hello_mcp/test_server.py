"""Tests for Tutorial 01 — Hello MCP."""

from shared.testing import mcp_client_for

SERVER = "tutorials/01_hello_mcp/server.py"


async def test_echo_returns_message():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("echo", {"message": "hello world"})
        assert result.content[0].text == "hello world"


async def test_echo_with_empty_string():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("echo", {"message": ""})
        assert result.content[0].text == ""


async def test_echo_tool_is_listed():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools.tools]
        assert "echo" in tool_names


async def test_echo_tool_has_description():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        echo_tool = next(t for t in tools.tools if t.name == "echo")
        desc = echo_tool.description.lower()
        assert "message" in desc or "return" in desc
