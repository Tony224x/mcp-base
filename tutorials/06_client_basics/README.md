# Tutorial 06 — Client Basics

## Writing an MCP Client

So far every tutorial has focused on the **server** side of MCP. This tutorial flips the perspective: you will write a **client** that connects to an MCP server, discovers its capabilities, and calls tools.

## Key Concepts

### StdioServerParameters

Tells the client how to launch the server process:

```python
from mcp import StdioServerParameters

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "tutorials/01_hello_mcp/server.py"],
)
```

- **command** — the executable to run (here `uv` to stay in the project venv)
- **args** — arguments passed to the command

### stdio_client

Opens a stdio connection to the server and yields read/write streams:

```python
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read_stream, write_stream):
    ...
```

The context manager starts the server subprocess and manages its lifecycle.

### ClientSession

Wraps the raw streams into a high-level MCP session:

```python
from mcp import ClientSession

async with ClientSession(read_stream, write_stream) as session:
    await session.initialize()
    ...
```

`initialize()` performs the MCP handshake — it **must** be called before any other method.

### Tool Discovery

```python
tools = await session.list_tools()
for tool in tools.tools:
    print(f"{tool.name}: {tool.description}")
```

`list_tools()` returns a `ListToolsResult` whose `.tools` attribute is a list of tool descriptors with `name`, `description`, and `inputSchema`.

### Calling a Tool

```python
result = await session.call_tool("echo", {"message": "Hello!"})
print(result.content[0].text)
```

`call_tool(name, arguments)` returns a `CallToolResult`:
- `.content` — a list of content objects (usually `TextContent` with a `.text` attribute)
- `.isError` — `True` if the tool raised an exception on the server side

## Running

```bash
# Run the client directly
uv run python tutorials/06_client_basics/client.py

# Automated tests
uv run pytest tutorials/06_client_basics/ -v
```
