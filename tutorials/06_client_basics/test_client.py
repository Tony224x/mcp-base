"""Tests for Tutorial 06 — Client Basics.

Uses the actual Tutorial 01 server to verify that a client can connect,
discover tools, and call them.
"""

from shared.testing import mcp_client_for

# The client in this tutorial talks to the Tutorial 01 server
SERVER = "tutorials/01_hello_mcp/server.py"


async def test_client_can_connect_and_list_tools():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        assert len(tools.tools) >= 1
        names = [t.name for t in tools.tools]
        assert "echo" in names


async def test_client_can_call_echo_tool():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("echo", {"message": "Hello from test!"})
        assert result.content[0].text == "Hello from test!"


async def test_client_echo_preserves_special_characters():
    async with mcp_client_for(SERVER) as client:
        msg = "Special chars: !@#$%^&*() and unicode: cafe\u0301"
        result = await client.call_tool("echo", {"message": msg})
        assert result.content[0].text == msg


async def test_client_tool_has_description():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        echo_tool = next(t for t in tools.tools if t.name == "echo")
        assert echo_tool.description is not None
        assert len(echo_tool.description) > 0
