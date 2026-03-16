"""Testing helpers for MCP servers.

Provides a reusable context manager to spin up a MCP server in-process
and return a connected ClientSession for testing.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def mcp_client_for(
    server_script: str,
    env: dict[str, str] | None = None,
) -> AsyncGenerator[ClientSession, None]:
    """Connect to a MCP server script and yield an initialized ClientSession.

    Usage:
        async with mcp_client_for("tutorials/01_hello_mcp/server.py") as client:
            result = await client.call_tool("echo", {"message": "hi"})
    """
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", server_script],
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session
