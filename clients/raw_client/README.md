# Raw MCP Client

A standalone MCP client that connects to a server via stdio and demonstrates the full discovery-and-call workflow using the Python SDK.

## Concepts

### StdioServerParameters

Configures how the client launches the server process:

```python
server_params = StdioServerParameters(
    command="uv",                          # executable
    args=["run", "python", server_script], # arguments
    env=None,                              # optional env vars
)
```

The client spawns the server as a subprocess and communicates over stdin/stdout using JSON-RPC.

### stdio_client

Establishes the stdio transport layer:

```python
async with stdio_client(server_params) as (read_stream, write_stream):
    ...
```

Returns a pair of async streams for reading server responses and writing client requests.

### ClientSession

Manages the MCP protocol session on top of the transport:

```python
async with ClientSession(read_stream, write_stream) as session:
    await session.initialize()  # MCP handshake
    ...
```

After initialization, the session provides methods for all MCP operations.

### Discovery Pattern

MCP clients discover server capabilities at runtime:

1. **`list_tools()`** — Returns available tools with names, descriptions, and JSON Schema input definitions
2. **`list_resources()`** — Returns available resources (data the server exposes)
3. **`list_prompts()`** — Returns available prompt templates

### Calling Tools

```python
result = await session.call_tool("tool_name", {"param": "value"})
for content in result.content:
    print(content.text)
```

Tool results contain a list of content blocks (text, images, etc.).

## Usage

```bash
uv run python clients/raw_client/client.py
```

## Tests

```bash
uv run pytest clients/raw_client/ -v
```
