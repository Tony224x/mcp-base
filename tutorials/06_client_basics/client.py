"""Tutorial 06 — Client Basics: A standalone MCP client.

Connects to the Tutorial 01 Hello MCP server, discovers its tools,
and calls the echo tool.
"""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Point at the Tutorial 01 server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "tutorials/01_hello_mcp/server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # --- Discover available tools ---
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # --- Call the echo tool ---
            message = "Hello from client!"
            result = await session.call_tool("echo", {"message": message})
            print(f"\nCalled echo with: {message!r}")
            print(f"Server replied:   {result.content[0].text!r}")


if __name__ == "__main__":
    asyncio.run(main())
