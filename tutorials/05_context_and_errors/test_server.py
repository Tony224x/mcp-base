"""Tests for Tutorial 05 — Context & Errors."""


from shared.testing import mcp_client_for

SERVER = "tutorials/05_context_and_errors/server.py"


# --- slow_process tests ---


async def test_slow_process_completes():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("slow_process", {"steps": 3})
        assert "3 steps done" in result.content[0].text


async def test_slow_process_single_step():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("slow_process", {"steps": 1})
        assert "1 steps done" in result.content[0].text


async def test_slow_process_invalid_steps():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("slow_process", {"steps": 0})
        assert result.isError


# --- divide tests ---


async def test_divide_normal():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("divide", {"a": 10, "b": 2})
        assert result.content[0].text == "5.0"


async def test_divide_returns_float():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("divide", {"a": 7, "b": 2})
        assert result.content[0].text == "3.5"


async def test_divide_by_zero_returns_error():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("divide", {"a": 1, "b": 0})
        assert result.isError


# --- validate_email tests ---


async def test_validate_email_valid():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool(
            "validate_email", {"email": "user@example.com"}
        )
        assert "Valid email" in result.content[0].text


async def test_validate_email_invalid_format():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool(
            "validate_email", {"email": "not-an-email"}
        )
        assert result.isError


async def test_validate_email_missing_domain():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool(
            "validate_email", {"email": "user@"}
        )
        assert result.isError


async def test_validate_email_plus_addressing_still_valid():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool(
            "validate_email", {"email": "user+tag@example.com"}
        )
        # Plus addressing is valid but triggers a warning
        assert "Valid email" in result.content[0].text


async def test_tools_are_listed():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        names = [t.name for t in tools.tools]
        assert "slow_process" in names
        assert "divide" in names
        assert "validate_email" in names
