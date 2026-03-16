# The MCP Ecosystem

## Overview

MCP is more than a protocol specification. It is surrounded by a growing
ecosystem of tools, SDKs, hosts, and community-built servers that make it
practical to build and use MCP-based systems. This document covers the key pieces
you will encounter.

---

## MCP Inspector

The **MCP Inspector** is a browser-based tool for interactively testing MCP
servers. It connects to a server, discovers its capabilities, and lets you call
tools, read resources, and invoke prompts through a web UI.

### How to Use It

In this project, every server and tutorial can be launched in the Inspector:

```bash
# Launch a tutorial server in the Inspector
uv run mcp dev tutorials/01_hello_mcp/server.py

# Launch a production server in the Inspector
uv run mcp dev servers/filesystem/server.py
```

This starts the server as a subprocess (stdio transport) and opens a browser
window where you can:

- See all registered tools, resources, and prompts
- Call tools with custom arguments and see results
- Read resources by URI
- Invoke prompts with parameters
- View the raw JSON-RPC messages being exchanged

The Makefile in this project has shortcuts for all servers:

```bash
make run-hello       # Tutorial 01
make run-tools       # Tutorial 02
make run-resources   # Tutorial 03
make run-prompts     # Tutorial 04
make run-context     # Tutorial 05
make run-filesystem  # Filesystem server
make run-web-fetch   # Web Fetch server
make run-sqlite      # SQLite Explorer server
make run-github      # API Bridge server
```

### When to Use It

- **During development:** Test your tools as you build them, without writing a
  client
- **Debugging:** Inspect exact JSON-RPC messages to diagnose issues
- **Demos:** Show stakeholders what an MCP server does

---

## Claude Desktop

**Claude Desktop** is Anthropic's desktop application for Claude. It has native
MCP support: you can configure MCP servers in a JSON file, and Claude will
automatically connect to them and use their tools during conversations.

### Configuration

Claude Desktop reads MCP server configuration from:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Example configuration to connect to servers from this project:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/mcp-base",
        "run", "python", "servers/filesystem/server.py"
      ],
      "env": {
        "MCP_SANDBOX_ROOT": "/path/to/allowed/directory"
      }
    },
    "sqlite": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/mcp-base",
        "run", "python", "servers/sqlite_explorer/server.py"
      ],
      "env": {
        "DB_PATH": "/path/to/database.db"
      }
    }
  }
}
```

Each entry specifies:

- **`command`**: The executable to run (here, `uv`)
- **`args`**: Command-line arguments to launch the server
- **`env`** (optional): Environment variables for the server process

Claude Desktop launches each server as a subprocess using stdio transport. The
servers appear as available tools in Claude's interface.

### How Claude Uses MCP Tools

When you chat with Claude in the desktop app and it has MCP servers connected:

1. Claude sees all available tools from all connected servers
2. When your question requires a tool, Claude decides which one to call
3. Claude Desktop calls the tool via MCP and shows you the result
4. Claude incorporates the result into its response

---

## Claude Code

**Claude Code** is Anthropic's CLI agent. It can also connect to MCP servers,
providing tool access in a terminal-based workflow.

Claude Code reads server configuration and connects to MCP servers similarly to
Claude Desktop, enabling tools to be used during command-line AI interactions.

---

## SDKs

Official and community SDKs make it easy to build MCP servers and clients in
different languages.

### Python SDK (`mcp`)

The primary SDK used in this project. Install it with:

```bash
pip install "mcp[cli]"
# or with uv (as in this project)
uv add "mcp[cli]"
```

The Python SDK provides:

| Component                    | Purpose                               |
|------------------------------|---------------------------------------|
| `mcp.server.fastmcp.FastMCP` | High-level server framework           |
| `mcp.ClientSession`          | Client session management             |
| `mcp.StdioServerParameters`  | Configuration for stdio connections   |
| `mcp.client.stdio`           | stdio client transport                |
| `mcp dev`                    | MCP Inspector CLI command             |
| `mcp run`                    | Run a server from CLI                 |

### TypeScript SDK (`@modelcontextprotocol/sdk`)

The official TypeScript/JavaScript SDK:

```bash
npm install @modelcontextprotocol/sdk
```

Useful for building MCP servers in Node.js, or MCP clients in web/Electron
applications.

### Other Languages

The MCP specification is language-agnostic. Community SDKs exist for Rust, Go,
Java, C#, and other languages. Check the
[MCP GitHub organization](https://github.com/modelcontextprotocol) for the
latest list.

---

## FastMCP

**FastMCP** is the high-level Python framework for building MCP servers. It is
part of the official Python SDK (`mcp` package) and is what this project uses
throughout.

### Why FastMCP?

Without FastMCP, building an MCP server means manually handling JSON-RPC
messages, constructing JSON Schemas, and managing the protocol state machine.
FastMCP reduces this to simple Python decorators:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("config://app")
def get_config() -> str:
    """Return app configuration."""
    return '{"version": "1.0"}'

@mcp.prompt()
def greeting(name: str) -> str:
    """Greet a user."""
    return f"Say hello to {name}"

if __name__ == "__main__":
    mcp.run()
```

### What FastMCP Handles for You

| Feature                        | How FastMCP helps                          |
|-------------------------------|-------------------------------------------|
| **JSON Schema generation**     | Derives from Python type hints             |
| **Tool registration**          | `@mcp.tool()` decorator                    |
| **Resource registration**      | `@mcp.resource(uri)` decorator             |
| **Prompt registration**        | `@mcp.prompt()` decorator                  |
| **Protocol handshake**         | Automatic capability negotiation           |
| **Message serialization**      | JSON-RPC handled transparently             |
| **Transport management**       | `mcp.run()` handles stdio or HTTP          |
| **Context injection**          | `Context` parameter auto-detected          |
| **Error handling**             | Python exceptions become MCP error responses|
| **Async support**              | Both sync and async functions work          |

---

## Testing MCP Servers

This project includes a testing helper in `shared/testing.py` that makes it easy
to write pytest tests for MCP servers:

```python
from shared.testing import mcp_client_for

async def test_echo_tool():
    async with mcp_client_for("tutorials/01_hello_mcp/server.py") as client:
        result = await client.call_tool("echo", {"message": "hello"})
        assert result.content[0].text == "hello"
```

The `mcp_client_for()` context manager:
1. Launches the server as a subprocess
2. Connects via stdio transport
3. Performs the initialization handshake
4. Yields an initialized `ClientSession`
5. Cleans up the subprocess on exit

Run all tests with:

```bash
uv run pytest -v
```

---

## Community Servers

The MCP ecosystem includes a growing number of pre-built servers for common
tools and services. Some examples:

| Server              | Purpose                                    |
|---------------------|--------------------------------------------|
| Filesystem          | Read/write files (sandboxed)               |
| PostgreSQL / SQLite | Database exploration and queries           |
| GitHub              | Repository operations, issues, PRs         |
| Slack               | Read/send messages                         |
| Google Drive        | Access documents and spreadsheets          |
| Brave Search        | Web search                                 |
| Puppeteer           | Browser automation                         |
| Docker              | Container management                       |

Many of these are available in the
[MCP Servers repository](https://github.com/modelcontextprotocol/servers).

---

## Project Structure of mcp-base

This project is organized as a progressive learning path:

```
mcp-base/
├── tutorials/                    # Progressive learning (01-06)
│   ├── 01_hello_mcp/            # Minimal MCP server
│   ├── 02_tools_deep_dive/      # Multiple tools, varied signatures
│   ├── 03_resources/            # Read-only data, URI templates
│   ├── 04_prompts/              # Prompt templates
│   ├── 05_context_and_errors/   # Context object, error handling
│   └── 06_client_basics/        # Writing an MCP client
│
├── servers/                      # Production-ready servers
│   ├── filesystem/              # Sandboxed file operations
│   ├── web_fetch/               # HTTP fetching, HTML parsing
│   ├── sqlite_explorer/         # Read-only SQLite access
│   └── api_bridge/              # REST API proxy
│
├── clients/                      # Different client approaches
│   ├── raw_client/              # Direct MCP protocol usage
│   ├── claude_api/              # Claude API + MCP tools (agent loop)
│   └── langchain_agent/        # LangChain + MCP integration
│
├── shared/                       # Shared utilities
│   ├── config.py                # Path and config helpers
│   ├── logging_config.py       # Logging (avoids stdout corruption)
│   └── testing.py              # pytest helper for MCP servers
│
├── docs/                         # Conceptual documentation (you are here)
├── pyproject.toml               # Project configuration
└── Makefile                     # Common commands
```

### Recommended Learning Path

1. Read `docs/00-what-is-mcp.md` through `docs/04-ecosystem.md` (this series)
2. Work through `tutorials/01` to `tutorials/06` in order
3. Study the production servers in `servers/`
4. Explore the different client approaches in `clients/`

---

## Official Resources

| Resource                                                                 | Description                        |
|--------------------------------------------------------------------------|------------------------------------|
| [modelcontextprotocol.io](https://modelcontextprotocol.io)              | Official MCP documentation         |
| [MCP Specification](https://modelcontextprotocol.io/specification)      | Full protocol specification        |
| [Python SDK](https://github.com/modelcontextprotocol/python-sdk)        | Official Python SDK (includes FastMCP) |
| [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)| Official TypeScript SDK            |
| [MCP Servers](https://github.com/modelcontextprotocol/servers)          | Collection of reference servers    |
| [MCP Inspector](https://github.com/modelcontextprotocol/inspector)      | Browser-based testing tool         |

---

## Summary

The MCP ecosystem provides everything you need to build, test, and deploy MCP
servers:

- **FastMCP** makes server development simple (decorators, auto-generated schemas)
- **MCP Inspector** provides interactive testing without writing a client
- **Claude Desktop** and **Claude Code** are ready-made hosts with MCP support
- **SDKs** in Python, TypeScript, and other languages handle protocol details
- **Community servers** provide pre-built integrations for common tools
- **This project** (`mcp-base`) ties it all together as a progressive learning
  path

Start building. The simplest MCP server is 10 lines of Python.
