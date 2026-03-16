# Tutorial 01 — Hello MCP

The simplest possible MCP server: one tool, one file, zero dependencies beyond `mcp[cli]`.

## What is MCP?

The **Model Context Protocol** (MCP) is an open standard that lets AI assistants
(Claude, GPT, etc.) communicate with external tools and data sources through a
uniform interface. Instead of each AI building custom integrations, MCP provides
a single protocol that any AI client can speak and any tool server can implement.

Key concepts:

| Concept      | Role                                                |
|--------------|-----------------------------------------------------|
| **Host**     | The AI application (Claude Desktop, an IDE, etc.)   |
| **Client**   | The protocol-level connector inside the host        |
| **Server**   | Your code — exposes tools, resources, and prompts   |

## What is FastMCP?

FastMCP is the high-level Python framework included in the `mcp` package.
It handles all the protocol plumbing so you can focus on writing plain Python
functions and decorating them:

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

That is the *entire* server. FastMCP automatically:

1. Inspects the function signature and docstring.
2. Generates a JSON Schema describing the tool's parameters.
3. Registers the tool so any MCP client can discover and call it.

## How `@mcp.tool()` works

When you decorate a function with `@mcp.tool()`:

- **Name** is derived from the function name (`echo`).
- **Description** is taken from the docstring.
- **Input schema** is built from the type hints (`message: str`).
- **Return value** is converted to a `TextContent` response.

The AI client sees this schema, decides when to call the tool, and sends a
structured request. Your function runs, returns a value, and MCP sends it back.

## Running the server

### With `mcp dev` (inspector UI)

```bash
mcp dev tutorials/01_hello_mcp/server.py
```

This opens a browser-based inspector where you can see the tool, send test
calls, and inspect the JSON-RPC messages.

### Directly via Python (stdio transport)

```bash
uv run python tutorials/01_hello_mcp/server.py
```

The server starts and listens on **stdio** — it reads JSON-RPC messages from
stdin and writes responses to stdout. This is the default transport and the one
used by Claude Desktop and most MCP clients.

## What is stdio transport?

MCP supports multiple transports. **Stdio** is the simplest:

- The client spawns the server as a child process.
- Communication happens over standard input/output pipes.
- No network ports, no HTTP, no configuration.

This makes stdio ideal for local development and desktop integrations. The
client sends a JSON-RPC request on the server's stdin; the server writes back
a JSON-RPC response on stdout.

## Running the tests

```bash
uv run pytest tutorials/01_hello_mcp/ -v
```

The tests use the shared helper `mcp_client_for` which spawns the server,
connects a real MCP client, and lets you call tools just like an AI would.

## Next steps

Head to [Tutorial 02 — Tools Deep Dive](../02_tools_deep_dive/) to explore
multiple tools, type coercion, optional parameters, and return types.
