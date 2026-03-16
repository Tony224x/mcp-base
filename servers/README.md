# MCP Servers

Production-ready MCP servers built with FastMCP. Each server is self-contained with its own `server.py`, `test_server.py`, and `README.md`.

## Available Servers

| Server | Directory | Description |
|---|---|---|
| **Filesystem** | [`filesystem/`](filesystem/) | Secure, sandboxed file operations (read, write, list, search, info) |
| **Web Fetch** | [`web_fetch/`](web_fetch/) | URL fetching with HTML text extraction, JSON retrieval, and availability checks |

## Quick Start

```bash
# Install all dependencies
uv sync --all-extras

# Run all server tests
uv run pytest servers/ -v

# Run a specific server (stdio transport)
uv run python servers/filesystem/server.py
uv run python servers/web_fetch/server.py
```

## Architecture

Each server follows a consistent structure:

```
servers/<name>/
    README.md        # Server documentation
    server.py        # FastMCP server with @mcp.tool() handlers
    test_server.py   # Tests using shared.testing.mcp_client_for()
```

All servers use the shared utilities from the `shared/` package:

- **`shared.testing`** — `mcp_client_for()` context manager for integration testing
- **`shared.config`** — Environment variable helpers and project path resolution
- **`shared.logging_config`** — File-based logging (avoids corrupting stdio JSON-RPC)

## Adding a New Server

1. Create a directory under `servers/` with `server.py`, `test_server.py`, and `README.md`.
2. Use `FastMCP` from `mcp.server.fastmcp` and decorate tool functions with `@mcp.tool()`.
3. Add `if __name__ == "__main__": mcp.run()` at the bottom of `server.py`.
4. Write tests using `mcp_client_for("servers/<name>/server.py")`.
5. Update this README with the new server entry.
