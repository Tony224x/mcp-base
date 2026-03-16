# MCP Architecture

## Overview

MCP follows a **client-server architecture** with three distinct roles and a
transport layer that connects them. Understanding these roles is essential to
building and debugging MCP systems.

```
┌─────────────────────────────────────────────┐
│                   HOST                       │
│  (Claude Desktop, IDE, your custom app)      │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ MCP      │  │ MCP      │  │ MCP      │   │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │         │
└───────┼──────────────┼──────────────┼─────────┘
        │              │              │
   Transport      Transport      Transport
   (stdio)        (stdio)        (HTTP+SSE)
        │              │              │
   ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐
   │ MCP      │  │ MCP      │  │ MCP      │
   │ Server A │  │ Server B │  │ Server C │
   │(filesys) │  │(database)│  │(remote)  │
   └──────────┘  └──────────┘  └──────────┘
```

## The Three Roles

### Host

The **host** is the application that the user interacts with. It embeds an LLM
and orchestrates the overall experience. The host is responsible for:

- Managing the LLM conversation
- Creating and managing MCP clients
- Deciding which MCP servers to connect to
- Presenting results to the user

**Examples of hosts:**

| Host              | Description                                    |
|-------------------|------------------------------------------------|
| Claude Desktop    | Anthropic's desktop app with native MCP support|
| Claude Code       | CLI agent that can connect to MCP servers       |
| IDE extensions    | VS Code, JetBrains with AI features            |
| Custom apps       | Your own application embedding an LLM          |

In this project, our clients in `clients/` act as simple hosts. For example,
`clients/claude_api/client.py` is a host that uses the Anthropic API as its LLM
and connects to MCP servers for tools.

### Client

The **MCP client** lives inside the host. It maintains a **1:1 connection** with
a single MCP server. A host typically creates one client per server it wants to
connect to.

The client is responsible for:

- Establishing a connection to an MCP server via a transport
- Performing the initialization handshake (capability negotiation)
- Sending requests to the server (list tools, call a tool, read a resource)
- Receiving responses and notifications from the server

In Python, the MCP client is provided by the `mcp` SDK:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Create connection parameters
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "tutorials/01_hello_mcp/server.py"],
)

# Connect: stdio_client manages the subprocess + transport
async with stdio_client(server_params) as (read_stream, write_stream):
    # ClientSession manages the protocol (handshake, requests, responses)
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()  # Handshake

        # Now use the session to interact with the server
        tools = await session.list_tools()
        result = await session.call_tool("echo", {"message": "hello"})
```

**Key point:** one client, one server. If a host wants to talk to three MCP
servers, it creates three clients.

### Server

The **MCP server** is a lightweight program that exposes capabilities (tools,
resources, prompts) via the MCP protocol. A server does not embed an LLM; it
simply makes functionality available for LLMs to use.

Servers are responsible for:

- Declaring their capabilities during initialization
- Responding to discovery requests (list tools, list resources, list prompts)
- Executing tool calls and returning results
- Serving resource content

In this project, servers use **FastMCP**, a high-level Python framework that
handles all protocol details with decorators:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

FastMCP automatically:
- Generates JSON Schema for tool parameters from Python type hints
- Registers tools, resources, and prompts
- Handles JSON-RPC message serialization
- Manages the transport layer

## The Connection Lifecycle

Here is how a client-server connection works, step by step:

```
Client                              Server
  │                                   │
  │──── initialize request ──────────>│  (1) Client sends capabilities
  │<─── initialize response ──────────│  (2) Server sends capabilities
  │──── initialized notification ────>│  (3) Handshake complete
  │                                   │
  │──── tools/list request ──────────>│  (4) Client discovers tools
  │<─── tools/list response ──────────│  (5) Server lists its tools
  │                                   │
  │──── tools/call request ──────────>│  (6) Client calls a tool
  │<─── tools/call response ──────────│  (7) Server returns result
  │                                   │
  │  ... (more requests/responses) ...│
  │                                   │
  │──── (close connection) ──────────>│  (8) Session ends
  │                                   │
```

### Phase 1: Initialization

The client and server exchange capabilities. The server announces what it
supports (tools, resources, prompts). The client announces what it supports
(e.g., ability to handle progress notifications). This is a negotiation -- both
sides learn what the other can do.

### Phase 2: Discovery

The client asks the server what capabilities are available. This is dynamic: the
client does not need to know in advance what a server offers. A typical discovery
sequence:

```python
# Discover tools
tools_result = await session.list_tools()

# Discover resources
resources_result = await session.list_resources()

# Discover prompts
prompts_result = await session.list_prompts()
```

### Phase 3: Operation

The client uses the discovered capabilities. For tools, this means calling them
with arguments and receiving results:

```python
result = await session.call_tool("read_file", {"path": "notes.txt"})
print(result.content[0].text)
```

For resources, this means reading their content:

```python
content = await session.read_resource("config://app")
```

### Phase 4: Shutdown

The connection is closed. With stdio transport, this means the server subprocess
is terminated. With HTTP transport, the HTTP connection is closed.

## Transport Layer

The transport layer defines **how** the client and server communicate. MCP
separates the protocol from the transport, so the same server logic works over
different transport mechanisms.

See `docs/03-transports.md` for a deep dive into transports.

**Quick summary:**

| Transport   | How it works                                    | Best for              |
|-------------|------------------------------------------------|-----------------------|
| **stdio**   | Server runs as subprocess; messages on stdin/stdout | Local tools, dev    |
| **HTTP+SSE**| Server is an HTTP endpoint; uses Server-Sent Events | Remote, shared servers |

## Full Request Flow

Here is the complete flow when an LLM uses an MCP tool, end to end:

```
User: "What files are in the sandbox?"
  │
  ▼
┌──────────────────────────────────┐
│ HOST (your app / Claude Desktop) │
│                                  │
│  1. User message → LLM          │
│  2. LLM decides to call a tool  │
│  3. Host routes to MCP Client   │
│     ┌─────────────────┐         │
│     │   MCP Client    │         │
│     │  4. call_tool() │         │
│     └───────┬─────────┘         │
└─────────────┼────────────────────┘
              │
         5. JSON-RPC over transport (stdio / HTTP)
              │
         ┌────┴────────────────┐
         │     MCP Server      │
         │  (Filesystem)       │
         │                     │
         │  6. Execute tool    │
         │     list_directory  │
         │  7. Read filesystem │
         │  8. Return result   │
         └────┬────────────────┘
              │
         9. JSON-RPC response over transport
              │
┌─────────────┼────────────────────┐
│     ┌───────┴─────────┐         │
│     │   MCP Client    │         │
│     │ 10. Parse result│         │
│     └───────┬─────────┘         │
│            11. Result → LLM     │
│            12. LLM generates    │
│                final answer     │
│            13. Display to user  │
└──────────────────────────────────┘
  │
  ▼
User sees: "The sandbox contains: [DIR] notes, [FILE] readme.txt"
```

## Agent Loop Pattern

When integrating MCP with an LLM API (like Claude's), the typical pattern is an
**agent loop**. The host keeps calling the LLM until it stops requesting tools:

```python
# Simplified agent loop (see clients/claude_api/client.py for the full version)
messages = [{"role": "user", "content": user_question}]

for turn in range(max_turns):
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        tools=claude_tools,       # MCP tools converted to Claude format
        messages=messages,
    )

    if response.stop_reason == "tool_use":
        # Claude wants to use a tool — call it via MCP
        for block in response.content:
            if block.type == "tool_use":
                mcp_result = await session.call_tool(block.name, block.input)
                # Feed result back to Claude
        # ... append tool results to messages, continue loop
    else:
        # Claude is done — print final answer
        break
```

## Relationship Between Components

| Component  | Creates           | Talks to        | Knows about        |
|------------|-------------------|-----------------|---------------------|
| Host       | MCP Clients       | LLM, User       | All clients          |
| Client     | Transport session | One server       | One server's caps    |
| Server     | Nothing           | Client (via transport) | Its own capabilities |
| Transport  | Connection        | Bytes/messages   | Nothing (just a pipe)|

## Key Design Principles

1. **Servers are stateless between calls.** Each tool call is independent. The
   server does not maintain conversation state (that is the host's job).

2. **Clients are 1:1 with servers.** No multiplexing. This keeps the protocol
   simple and makes it easy to reason about security boundaries.

3. **Discovery is dynamic.** Clients learn what a server can do at runtime.
   This enables generic AI applications that work with any MCP server.

4. **Transport is pluggable.** The same server code works over stdio or HTTP.
   New transports can be added without changing server logic.

## Further Reading

- `docs/02-primitives.md` -- the three types of capabilities servers expose
- `docs/03-transports.md` -- deep dive into stdio and HTTP transports
- [MCP Specification: Architecture](https://modelcontextprotocol.io/docs/concepts/architecture)
