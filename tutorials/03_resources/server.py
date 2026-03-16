"""Tutorial 03 — Resources: Expose read-only data via MCP resources."""

import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Resources")

# ── Static resources ─────────────────────────────────────────────────────


@mcp.resource("config://app")
def get_app_config() -> str:
    """Return the application configuration as JSON."""
    config = {
        "app_name": "MCP Tutorial App",
        "version": "1.0.0",
        "debug": False,
        "max_connections": 100,
        "features": ["tools", "resources", "prompts"],
    }
    return json.dumps(config, indent=2)


@mcp.resource("info://server")
def get_server_info() -> str:
    """Return human-readable information about this server."""
    return (
        "MCP Resources Tutorial Server\n"
        "=============================\n"
        "This server demonstrates static resources and resource templates.\n"
        "It is part of the mcp-base tutorial series.\n"
    )


# ── Resource templates ───────────────────────────────────────────────────

# Fake user database for the template demo.
_USERS = {
    "1": {"name": "Alice", "email": "alice@example.com", "role": "admin"},
    "2": {"name": "Bob", "email": "bob@example.com", "role": "editor"},
    "3": {"name": "Charlie", "email": "charlie@example.com", "role": "viewer"},
}


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Return the profile for a given user ID.

    If the user is not found, returns an error message.
    """
    user = _USERS.get(user_id)
    if user is None:
        return json.dumps({"error": f"User {user_id} not found"})
    return json.dumps({"user_id": user_id, **user}, indent=2)


if __name__ == "__main__":
    mcp.run()
