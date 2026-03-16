# Tutorial 05 — Context & Errors

## The Context Object

When a tool handler accepts a `ctx: Context` parameter, FastMCP automatically injects a **Context** object that provides a communication channel back to the client while the tool is executing.

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("MyServer")

@mcp.tool()
async def my_tool(param: str, ctx: Context) -> str:
    await ctx.info("Starting work...")
    return "done"
```

Tools that use Context **must** be `async` functions.

## Logging Levels

The Context object provides structured logging methods that send log messages back to the client:

| Method | Purpose |
|---|---|
| `await ctx.debug(msg)` | Low-level debugging information |
| `await ctx.info(msg)` | General informational messages |
| `await ctx.warning(msg)` | Warnings about potential issues |
| `await ctx.error(msg)` | Error conditions (non-fatal) |

These log messages are delivered to the client in real-time, allowing it to display progress or store logs.

## Progress Reporting

For long-running operations, report progress so the client can show a progress indicator:

```python
@mcp.tool()
async def slow_process(steps: int, ctx: Context) -> str:
    for i in range(1, steps + 1):
        await ctx.report_progress(i, steps)   # current, total
        await ctx.info(f"Step {i}/{steps}")
    return "done"
```

`report_progress(current, total)` takes two arguments:
- **current** — how many units of work are complete
- **total** — total units of work expected

## Error Handling

In FastMCP, raising a Python exception inside a tool handler causes the framework to return an **error result** to the client instead of a normal result. The client receives `isError=True` along with the error message.

```python
@mcp.tool()
async def divide(a: float, b: float) -> str:
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return str(a / b)
```

Best practices:
- **Raise `ValueError`** for invalid input — it communicates the problem clearly.
- **Use `ctx.warning()`** for non-fatal issues that should be logged but do not prevent completion.
- **Return a string result** for successful operations; raise an exception for failures.

## Running

```bash
# Interactive inspection
uv run mcp dev tutorials/05_context_and_errors/server.py

# Automated tests
uv run pytest tutorials/05_context_and_errors/ -v
```
