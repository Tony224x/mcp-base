# MCP Transports

## Overview

The **transport layer** defines how MCP clients and servers communicate. MCP
separates protocol logic from transport: the same server code works over
different transports without modification. The protocol messages are the same;
only the delivery mechanism changes.

MCP currently defines two standard transports:

| Transport         | Description                                | Best for                  |
|-------------------|--------------------------------------------|--------------------------|
| **stdio**         | Server runs as subprocess, uses stdin/stdout | Local tools, development |
| **Streamable HTTP** | Server runs as HTTP endpoint with SSE     | Remote / shared servers  |

Both transports carry the same payload: **JSON-RPC 2.0** messages.

---

## JSON-RPC 2.0: The Message Format

Before diving into transports, it helps to understand what travels over them.
MCP uses [JSON-RPC 2.0](https://www.jsonrpc.org/specification) as its message
format. Every MCP interaction is a JSON-RPC message.

### Request

A client sends a request to the server:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": { "a": 40, "b": 2 }
  }
}
```

### Response

The server replies with a response (same `id`):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "42" }
    ]
  }
}
```

### Notification

Either side can send a notification (no `id`, no response expected):

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc",
    "progress": 3,
    "total": 10
  }
}
```

### Error

If something goes wrong, the server returns an error:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Division by zero is not allowed"
  }
}
```

You never construct these messages manually when using FastMCP or the Python
client SDK. They handle serialization and deserialization for you. But
understanding the format is useful for debugging.

---

## stdio Transport

### How It Works

The **stdio** transport is the simplest and most common. The client launches the
server as a **subprocess** and communicates via standard input and output:

```
┌────────────┐                      ┌────────────┐
│   Client   │ ── JSON-RPC on ───> │   Server   │
│            │     stdout/stdin     │ (subprocess)│
│            │ <── JSON-RPC on ──── │            │
└────────────┘     stdout/stdin     └────────────┘
```

More precisely:

- **Client -> Server:** Client writes JSON-RPC messages to the server's **stdin**
- **Server -> Client:** Server writes JSON-RPC messages to its own **stdout**

Each message is a single line of JSON, terminated by a newline.

### Why stdio?

- **No networking required.** Everything happens on the local machine.
- **No port conflicts.** No need to pick a port or deal with firewalls.
- **Process isolation.** The server runs in its own process with its own
  permissions.
- **Simple lifecycle.** Client starts the server process, uses it, then
  terminates it.

### Important: Do Not Print to stdout

When writing an MCP server that uses stdio transport, **never use `print()` or
write to `sys.stdout` / `sys.stderr` directly**. Any output that is not a valid
JSON-RPC message will corrupt the protocol stream and break the connection.

Use the `Context` object for logging instead:

```python
# BAD: corrupts the stdio transport
print("Debug: processing request")

# GOOD: logs via the MCP protocol
await ctx.info("Debug: processing request")
```

This project uses a logging configuration (`shared/logging_config.py`) that
directs logs to files rather than stdout/stderr.

### Using stdio in Python

**Server side** -- just call `mcp.run()`. FastMCP defaults to stdio:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def greet(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()  # Listens on stdin/stdout
```

**Client side** -- use `StdioServerParameters` and `stdio_client`:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "path/to/server.py"],
)

async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        # Use session...
```

The `stdio_client` context manager:
1. Spawns the server as a subprocess
2. Connects to its stdin/stdout
3. Provides read/write streams to create a `ClientSession`
4. Terminates the subprocess when the context exits

### Using stdio with the MCP Inspector

The MCP Inspector (a browser-based debugging tool) uses stdio by default:

```bash
uv run mcp dev tutorials/01_hello_mcp/server.py
```

This launches the server as a subprocess and opens a web UI where you can
interactively list tools, call them, and inspect the JSON-RPC messages.

---

## Streamable HTTP Transport (HTTP + SSE)

### How It Works

The **Streamable HTTP** transport runs the server as an HTTP endpoint. The client
communicates with it using standard HTTP requests, and the server can push
messages back to the client using **Server-Sent Events (SSE)**.

```
┌────────────┐                          ┌────────────┐
│   Client   │ ── HTTP POST ─────────> │   Server   │
│            │    (JSON-RPC request)    │  (HTTP     │
│            │                          │   endpoint)│
│            │ <── SSE stream ──────── │            │
│            │    (JSON-RPC responses   │            │
│            │     + notifications)     │            │
└────────────┘                          └────────────┘
```

### Key Characteristics

- **Client to server:** Standard HTTP POST requests containing JSON-RPC messages
- **Server to client:** Server-Sent Events (SSE) for streaming responses and
  notifications
- **Stateful sessions:** The server can maintain session state across requests
  using session tokens
- **Networkable:** Works across machines, through proxies, and over the internet

### When to Use HTTP Transport

| Scenario                              | Use stdio | Use HTTP |
|---------------------------------------|-----------|----------|
| Local development / testing           | Yes       |          |
| Server on the same machine            | Yes       |          |
| Server on a different machine         |           | Yes      |
| Multiple clients sharing one server   |           | Yes      |
| Server behind a firewall / VPN        |           | Yes      |
| Claude Desktop integration            | Yes       |          |
| Production deployment                 |           | Yes      |
| CI/CD pipeline                        | Either    | Either   |

### Running a Server with HTTP Transport

FastMCP can serve over HTTP by specifying the transport:

```python
if __name__ == "__main__":
    mcp.run(transport="sse")  # Start HTTP+SSE server
```

Or from the command line:

```bash
uv run mcp run path/to/server.py --transport sse
```

The server will start an HTTP server (typically on port 8000) that accepts MCP
connections.

---

## Transport Comparison

| Feature              | stdio                          | Streamable HTTP              |
|----------------------|-------------------------------|------------------------------|
| **Setup**            | Zero config                    | Needs port/host config       |
| **Networking**       | Local only                     | Local or remote              |
| **Concurrency**      | One client per server process  | Multiple clients             |
| **Lifecycle**        | Client manages server process  | Server runs independently    |
| **Debugging**        | MCP Inspector uses this        | Standard HTTP debugging tools|
| **Security**         | OS process isolation           | Needs auth/TLS for production|
| **Complexity**       | Very low                       | Moderate                     |

## How Transports Relate to the Rest of MCP

The beauty of MCP's design is that **transports are invisible to your server
logic**. The same `@mcp.tool()` decorated function works over stdio or HTTP
without any changes. The transport only affects:

1. How the server is started (`mcp.run()` vs. `mcp.run(transport="sse")`)
2. How the client connects (`stdio_client` vs. HTTP client)
3. Deployment concerns (subprocess vs. HTTP server)

Your tool implementations, resource definitions, and prompt templates are
completely transport-agnostic.

---

## Debugging Transport Issues

### stdio Debugging Tips

1. **Corrupted stream:** If you see `JSONDecodeError` or the client disconnects
   immediately, check that your server never writes to stdout (no `print()`
   statements).

2. **Server not starting:** Make sure the command and args in
   `StdioServerParameters` are correct. The `command` must be in PATH.

3. **Inspect the wire:** Use `MCP_LOG_LEVEL=debug` or the MCP Inspector to see
   raw JSON-RPC messages.

### HTTP Debugging Tips

1. **Connection refused:** Check the server is running and the port is correct.

2. **SSE not connecting:** Some proxies/firewalls strip SSE headers. Test with a
   direct connection first.

3. **Use standard HTTP tools:** `curl`, browser dev tools, or Postman can inspect
   the HTTP requests.

## Further Reading

- `docs/01-architecture.md` -- where transports fit in the overall architecture
- `docs/04-ecosystem.md` -- tools for testing and debugging MCP (including the
  Inspector)
- [MCP Specification: Transports](https://modelcontextprotocol.io/docs/concepts/transports)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
