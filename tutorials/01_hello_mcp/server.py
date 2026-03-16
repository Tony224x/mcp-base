"""Tutorial 01 — Hello MCP: The simplest possible MCP server."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloMCP")


@mcp.tool()
def echo(message: str) -> str:
    """Return the exact message that was received."""
    return message


if __name__ == "__main__":
    mcp.run()
