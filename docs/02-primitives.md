# MCP Primitives: Tools, Resources, and Prompts

## Overview

MCP servers expose capabilities through three **primitives**. Each primitive
serves a different purpose and is controlled by a different part of the system:

| Primitive      | Controlled by  | Direction        | Analogy               |
|----------------|---------------|------------------|-----------------------|
| **Tools**      | Model (LLM)   | Client -> Server | Function calls / POST |
| **Resources**  | Application   | Client -> Server | GET endpoints / files |
| **Prompts**    | User          | Client -> Server | Templates / shortcuts |

Understanding who controls each primitive is key to designing good MCP servers.

---

## Tools

### What Are Tools?

Tools are **functions that the LLM can call**. They are the most common MCP
primitive and the one closest to "function calling" in LLM APIs. When a server
exposes a tool, it tells the client:

- The tool's name
- A natural language description (for the LLM to understand when to use it)
- A JSON Schema describing the expected input parameters
- The output format

The **LLM decides** when to call a tool based on the user's request and the
tool's description. This is what makes tools "model-controlled."

### Defining Tools with FastMCP

In this project, tools are defined using the `@mcp.tool()` decorator. FastMCP
automatically generates the JSON Schema from Python type hints:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ToolsDeepDive")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate Body Mass Index from weight (kg) and height (m).

    Returns a formatted string with the BMI value and category.
    """
    if height_m <= 0:
        return "Error: height must be positive."
    bmi = weight_kg / (height_m ** 2)
    category = "normal weight" if 18.5 <= bmi < 25 else "other"
    return f"BMI: {bmi:.1f} ({category})"
```

### How JSON Schema is Generated

When you write `def add(a: int, b: int) -> int`, FastMCP generates this schema
automatically:

```json
{
  "name": "add",
  "description": "Add two integers and return the sum.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": { "type": "integer" },
      "b": { "type": "integer" }
    },
    "required": ["a", "b"]
  }
}
```

Python type hints map to JSON Schema types (`str` -> `string`, `int` ->
`integer`, `float` -> `number`, `bool` -> `boolean`, `list[str]` -> array of
strings). Parameters with default values become optional in the schema.

### Calling Tools from a Client

Clients discover and call tools at runtime:

```python
# Discover tools
tools_result = await session.list_tools()
for tool in tools_result.tools:
    print(f"{tool.name}: {tool.description}")
    print(f"  Schema: {tool.inputSchema}")

# Call a tool
result = await session.call_tool("add", {"a": 40, "b": 2})
print(result.content[0].text)  # "42"
```

### Async Tools and Context

Tools can be async and can accept a `Context` object for progress reporting and
logging:

```python
from mcp.server.fastmcp import Context, FastMCP

@mcp.tool()
async def slow_process(steps: int, ctx: Context) -> str:
    """Simulate a multi-step process with progress reporting."""
    if steps < 1:
        raise ValueError("steps must be at least 1")

    await ctx.info(f"Starting process with {steps} steps")

    for i in range(1, steps + 1):
        await ctx.report_progress(i, steps)
        await ctx.info(f"Completed step {i}/{steps}")

    return f"Process completed: {steps} steps done"
```

The `Context` parameter is **not** exposed in the JSON Schema -- FastMCP detects
it and injects it automatically. The client never sees it.

### Error Handling in Tools

Tools can raise exceptions to signal errors. FastMCP catches them and returns
them as error responses to the client:

```python
@mcp.tool()
async def divide(a: float, b: float) -> str:
    """Divide a by b. Raises an error when b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return str(a / b)
```

### Real-World Tool Examples

See `servers/filesystem/server.py` for tools like `read_file`, `write_file`,
`search_files` (sandboxed file operations), and `servers/web_fetch/server.py`
for async tools like `fetch_url` and `fetch_json`.

---

## Resources

### What Are Resources?

Resources are **read-only data** that the application can access. Think of them
as GET endpoints: they have a URI, they return content, and they do not modify
anything.

Resources are "application-controlled" -- the host application decides when to
read them, not the LLM. This is an important distinction from tools. A common
pattern is for the host to read resources to provide context to the LLM, rather
than the LLM calling them directly.

### Defining Resources

Resources are identified by URIs. FastMCP uses the `@mcp.resource()` decorator:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Resources")

@mcp.resource("config://app")
def get_app_config() -> str:
    """Return the application configuration as JSON."""
    config = {
        "app_name": "MCP Tutorial App",
        "version": "1.0.0",
        "debug": False,
        "features": ["tools", "resources", "prompts"],
    }
    return json.dumps(config, indent=2)

@mcp.resource("info://server")
def get_server_info() -> str:
    """Return human-readable information about this server."""
    return "MCP Resources Tutorial Server\n..."
```

### Resource Templates

Resources can have **URI templates** with parameters, similar to URL path
parameters in a web framework:

```python
_USERS = {
    "1": {"name": "Alice", "email": "alice@example.com", "role": "admin"},
    "2": {"name": "Bob",   "email": "bob@example.com",   "role": "editor"},
}

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Return the profile for a given user ID."""
    user = _USERS.get(user_id)
    if user is None:
        return json.dumps({"error": f"User {user_id} not found"})
    return json.dumps({"user_id": user_id, **user}, indent=2)
```

When a client reads `users://1/profile`, FastMCP extracts `user_id="1"` and
passes it to the function.

### Reading Resources from a Client

```python
# List available resources
resources = await session.list_resources()
for res in resources.resources:
    print(f"  {res.uri}: {res.name}")

# Read a specific resource
content = await session.read_resource("config://app")
```

### Resources vs. Tools

A common question: when should I use a resource vs. a tool?

| Aspect             | Resource                          | Tool                            |
|--------------------|------------------------------------|--------------------------------|
| **Purpose**        | Expose data                        | Perform actions                 |
| **Mutates state?** | No (read-only)                     | Can mutate state                |
| **Parameters**     | URI template variables             | Full JSON Schema                |
| **Who invokes?**   | Application (host)                 | Model (LLM)                    |
| **Analogous to**   | GET endpoint, file read            | POST endpoint, function call   |

**Rule of thumb:** if it reads data, make it a resource. If it performs an action
or takes complex input, make it a tool.

### Real-World Resource Example

From `servers/sqlite_explorer/server.py`:

```python
@mcp.resource("db://schema")
def get_schema() -> str:
    """Return the full database schema (all CREATE TABLE statements)."""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
        )
        statements = [row["sql"] for row in cursor.fetchall()]
        return "\n\n".join(statements)
    finally:
        conn.close()
```

The schema is read-only data that provides context. A host might read this
resource and include it in the LLM's system prompt so the model knows what tables
are available before the user even asks a question.

---

## Prompts

### What Are Prompts?

Prompts are **pre-built, reusable prompt templates** that a server can expose.
They are "user-controlled" -- the user (or application UI) selects and invokes
them, typically from a menu or command palette.

Prompts are the least common primitive but very useful for standardizing how
users interact with an LLM through a particular server. Think of them as
"recipes" or "shortcuts" for common interactions.

### Defining Prompts

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("PromptServer")

@mcp.prompt()
def greeting(name: str) -> str:
    """Generate a warm greeting for a user."""
    return f"Greet the user named {name} warmly"

@mcp.prompt()
def code_review(code: str, language: str = "python") -> list[base.Message]:
    """Review code in a given programming language."""
    return [
        base.UserMessage(
            content=f"Please review the following {language} code for correctness, "
            f"style, and potential improvements:\n\n```{language}\n{code}\n```"
        ),
    ]

@mcp.prompt()
def summarize(text: str, style: str = "concise") -> str:
    """Summarize text in a given style."""
    return f"Summarize the following text in a {style} style:\n\n{text}"
```

### Prompt Return Types

Prompts can return:

- **A string** -- becomes a single user message
- **A list of `Message` objects** -- for multi-turn or multi-role conversations

The `Message` objects allow you to construct complex prompt structures with
specific roles:

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt()
def debug_session(error: str) -> list[base.Message]:
    """Start a debugging session for an error."""
    return [
        base.UserMessage(content=f"I'm seeing this error: {error}"),
        base.AssistantMessage(content="I'll help you debug that. Let me analyze the error."),
        base.UserMessage(content="Please suggest potential causes and fixes."),
    ]
```

### Using Prompts from a Client

```python
# List available prompts
prompts = await session.list_prompts()
for prompt in prompts.prompts:
    print(f"  {prompt.name}: {prompt.description}")

# Get a prompt with arguments
result = await session.get_prompt("code_review", {
    "code": "def add(a, b): return a + b",
    "language": "python",
})
# result.messages contains the prompt messages to send to the LLM
```

---

## Comparison Table

| Aspect               | Tools                      | Resources                  | Prompts                    |
|----------------------|---------------------------|---------------------------|---------------------------|
| **Purpose**          | Perform actions            | Expose data                | Template conversations    |
| **Controlled by**    | Model (LLM)               | Application (host)         | User                      |
| **Input**            | JSON Schema (from types)   | URI (with template vars)   | Named parameters          |
| **Output**           | Text / structured content  | Text / binary content      | Message list              |
| **Mutates state?**   | Can (write files, etc.)    | No (read-only)             | No                        |
| **Discovery**        | `list_tools()`             | `list_resources()`         | `list_prompts()`          |
| **Invocation**       | `call_tool(name, args)`    | `read_resource(uri)`       | `get_prompt(name, args)`  |
| **Decorator**        | `@mcp.tool()`              | `@mcp.resource(uri)`       | `@mcp.prompt()`           |
| **Analogy**          | POST endpoint / RPC        | GET endpoint / file        | Saved query / macro       |

## When to Use What

**Use a Tool when:**
- The LLM needs to perform an action (create a file, run a query, call an API)
- The operation takes structured input (multiple parameters, complex types)
- The operation might change state

**Use a Resource when:**
- You want to expose read-only data (config, schema, documentation)
- The data is identified by a URI pattern
- The host/application should control access (not the LLM)

**Use a Prompt when:**
- You want to provide reusable conversation starters
- Users should be able to select from predefined interaction patterns
- You want to standardize how users ask the LLM for certain things

## Combining Primitives

A single server can expose all three primitives. This is common in production
servers. For example, the SQLite Explorer in this project exposes:

- **Tools:** `query`, `list_tables`, `describe_table` -- for the LLM to explore
  the database
- **Resources:** `db://schema` -- for the host to provide database context

This combination lets the host pre-load the schema as context (resource), while
the LLM dynamically queries the database as needed (tools).

## Further Reading

- `tutorials/02_tools_deep_dive/` -- hands-on tool examples
- `tutorials/03_resources/` -- hands-on resource examples
- `tutorials/04_prompts/` -- hands-on prompt examples
- `docs/03-transports.md` -- how primitives are communicated over the wire
- [MCP Specification: Primitives](https://modelcontextprotocol.io/docs/concepts/tools)
