"""Tutorial 05 — Context & Errors: Using the Context object and handling errors."""

import re

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("ContextErrorServer")


@mcp.tool()
async def slow_process(steps: int, ctx: Context) -> str:
    """Simulate a multi-step process with progress reporting.

    Reports progress after each step via the Context object.
    """
    if steps < 1:
        raise ValueError("steps must be at least 1")

    await ctx.info(f"Starting process with {steps} steps")

    for i in range(1, steps + 1):
        await ctx.report_progress(i, steps)
        await ctx.info(f"Completed step {i}/{steps}")

    return f"Process completed: {steps} steps done"


@mcp.tool()
async def divide(a: float, b: float) -> str:
    """Divide a by b. Raises an error when b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    result = a / b
    return str(result)


@mcp.tool()
async def validate_email(email: str, ctx: Context) -> str:
    """Validate an email address format and flag suspicious patterns."""
    # Basic format check
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")

    # Warn about suspicious patterns
    if "+" in email.split("@")[0]:
        await ctx.warning(f"Email uses plus-addressing: {email}")

    if email.endswith(".test") or email.endswith(".example"):
        await ctx.warning(f"Email uses a reserved test domain: {email}")

    local_part = email.split("@")[0]
    if len(local_part) > 64:
        await ctx.warning("Local part exceeds 64 characters")

    await ctx.info(f"Email validated: {email}")
    return f"Valid email: {email}"


if __name__ == "__main__":
    mcp.run()
