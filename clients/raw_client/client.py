"""Raw MCP client — Connect to a server, discover capabilities, and call tools."""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_client(server_script: str = "tutorials/01_hello_mcp/server.py"):
    """Connect to an MCP server, discover tools, and call them."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", server_script],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Discovery
            print("=== Available Tools ===")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"  {tool.name}: {tool.description}")
                if tool.inputSchema:
                    props = tool.inputSchema.get("properties", {})
                    for pname, pinfo in props.items():
                        print(f"    - {pname}: {pinfo.get('type', '?')}")

            # Call echo tool
            print("\n=== Calling echo ===")
            result = await session.call_tool("echo", {"message": "Hello from raw client!"})
            for content in result.content:
                print(f"  Result: {content.text}")

            # Try listing resources if available
            try:
                resources_result = await session.list_resources()
                if resources_result.resources:
                    print("\n=== Available Resources ===")
                    for res in resources_result.resources:
                        print(f"  {res.uri}: {res.name}")
            except Exception:
                pass

            # Try listing prompts if available
            try:
                prompts_result = await session.list_prompts()
                if prompts_result.prompts:
                    print("\n=== Available Prompts ===")
                    for prompt in prompts_result.prompts:
                        print(f"  {prompt.name}: {prompt.description}")
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(run_client())
