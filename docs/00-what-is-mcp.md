# What is the Model Context Protocol (MCP)?

## The Problem

Large Language Models are powerful, but they live in a bubble. By default, an LLM
has no way to read your files, query your database, call an API, or interact with
the world beyond its training data. Every time you want to connect an AI
application to a new data source or tool, you need to write custom integration
code -- different for every AI provider, different for every tool.

This creates an **M x N problem**: if you have M AI applications and N tools, you
end up writing M x N integrations. Each is a bespoke, fragile bridge.

```
Without MCP:

  Claude Desktop ──custom code──> Filesystem
  Claude Desktop ──custom code──> Database
  Claude Desktop ──custom code──> GitHub API
  VS Code Copilot ──custom code──> Filesystem   (different code!)
  VS Code Copilot ──custom code──> Database      (different code!)
  VS Code Copilot ──custom code──> GitHub API    (different code!)
  Custom App      ──custom code──> ...           (even more code!)
```

## The Solution: MCP

The **Model Context Protocol (MCP)** is an open standard that provides a
universal interface between AI applications and external capabilities. Instead of
writing custom integrations for every combination, you write each side once:

- **Tool authors** write one MCP server that exposes their capability.
- **App authors** write one MCP client that speaks the protocol.

Any MCP client can talk to any MCP server. The M x N problem becomes M + N.

```
With MCP:

  Claude Desktop ─┐
  VS Code Copilot ─┤─── MCP Protocol ───┤─ Filesystem Server
  Custom App      ─┘                    ├─ Database Server
                                        └─ GitHub API Server
```

## The USB-C Analogy

MCP is like **USB-C for AI**.

Before USB-C, every device had its own charging cable and data connector --
micro-USB, Lightning, barrel jacks, proprietary ports. You needed a different
cable for every device. USB-C replaced all of that with one universal connector.

MCP does the same thing for AI:

| USB-C World          | MCP World                          |
|----------------------|------------------------------------|
| USB-C port           | MCP protocol                       |
| Laptop / phone       | AI host (Claude Desktop, IDE, app) |
| Charger / peripheral | MCP server (tool, data source)     |
| USB-C cable          | Transport (stdio, HTTP)            |

One standard. Any AI app. Any tool. They just connect.

## Why Does MCP Exist?

MCP was created to solve several interrelated problems:

### 1. Interoperability

Before MCP, every AI provider had its own way to call tools. OpenAI has function
calling, Anthropic has tool use, LangChain has its own tool abstraction. MCP
provides a **provider-agnostic** protocol: a tool written as an MCP server works
with Claude Desktop, with a custom Python client, with a LangChain agent -- no
changes needed.

### 2. Composability

MCP servers are modular. You can connect multiple servers to a single AI
application. Need file access, database queries, and web browsing? Connect three
MCP servers. Each server is a self-contained unit with clear boundaries.

In this project, for instance, we have independent servers for:

- **Filesystem** -- sandboxed file operations (`servers/filesystem/`)
- **Web Fetch** -- retrieve and parse web pages (`servers/web_fetch/`)
- **SQLite Explorer** -- read-only database exploration (`servers/sqlite_explorer/`)
- **API Bridge** -- connect to REST APIs (`servers/api_bridge/`)

An AI host can connect to all of them simultaneously.

### 3. Security Boundaries

Each MCP server runs in its own process with its own permissions. A filesystem
server can be sandboxed to a specific directory. A database server can enforce
read-only access. The LLM never gets direct access to your system -- it can only
use the capabilities that a server explicitly exposes.

For example, our filesystem server restricts all operations to a sandbox
directory:

```python
def _safe_resolve(path: str) -> Path:
    """Resolve a user-supplied path within the sandbox, rejecting traversals."""
    root = _sandbox_root()
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path '{path}' escapes the sandbox root. Access denied.")
    return resolved
```

### 4. Discoverability

MCP servers describe their own capabilities. A client can connect to a server and
ask: "What tools do you have? What are their parameters? What resources do you
expose?" This makes integration dynamic -- the AI can discover and use tools it
has never seen before, as long as they follow the protocol.

```python
# A client discovering tools at runtime
tools_result = await session.list_tools()
for tool in tools_result.tools:
    print(f"  {tool.name}: {tool.description}")
    # Each tool includes a JSON Schema describing its parameters
```

## Key Benefits at a Glance

| Benefit           | Description                                                 |
|-------------------|-------------------------------------------------------------|
| **Universal**     | One protocol for all AI apps and all tools                  |
| **Modular**       | Plug servers in and out without changing application code    |
| **Secure**        | Each server controls its own permissions and boundaries     |
| **Discoverable**  | Clients dynamically learn what a server can do              |
| **Open standard** | Not locked to any vendor; community-driven ecosystem        |
| **Simple**        | A minimal server is ~10 lines of Python (see below)         |

## A Minimal MCP Server

Here is the simplest possible MCP server, from this project's first tutorial
(`tutorials/01_hello_mcp/server.py`):

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloMCP")

@mcp.tool()
def echo(message: str) -> str:
    """Return the exact message that was received."""
    return message

if __name__ == "__main__":
    mcp.run()
```

That is a complete, functional MCP server. It exposes one tool (`echo`) that any
MCP client can discover and call. The `@mcp.tool()` decorator handles all the
protocol details: registering the tool, generating a JSON Schema from the Python
type hints, serializing requests and responses.

## Who Created MCP?

MCP was created by **Anthropic** and released as an **open standard**. The
specification, SDKs, and reference implementations are all open source. The
protocol is designed to be vendor-neutral: while Anthropic created it, anyone can
build MCP clients and servers.

## What You Will Learn in This Project

This project (`mcp-base`) is a hands-on learning path for MCP:

1. **Tutorials** (`tutorials/01` through `tutorials/06`): Build MCP servers and
   clients from scratch, one concept at a time.
2. **Production servers** (`servers/`): Real-world MCP servers with security,
   error handling, and testing.
3. **Clients** (`clients/`): Different ways to consume MCP servers -- raw
   protocol, Claude API integration, LangChain agents.

Start with `tutorials/01_hello_mcp/` and work your way forward.

## Further Reading

- [MCP Specification](https://modelcontextprotocol.io) -- the official docs
- [MCP GitHub Organization](https://github.com/modelcontextprotocol) -- SDKs and
  reference implementations
- `docs/01-architecture.md` -- how MCP is structured (next in this series)
