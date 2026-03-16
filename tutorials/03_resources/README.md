# Tutorial 03 — Resources

Resources let an MCP server expose **read-only data** that AI clients can
retrieve on demand. Unlike tools (which *do* something), resources represent
data the AI can *read* — configuration, documents, database records, etc.

## What are Resources?

In MCP, a **Resource** is a piece of data identified by a URI. The client can:

1. **List** available resources (`resources/list`).
2. **Read** a specific resource by URI (`resources/read`).

Resources are analogous to GET endpoints in a REST API. They do not accept
arbitrary input or cause side effects — they simply return data.

## URI schemes

Every resource has a URI that uniquely identifies it. MCP does not prescribe
any particular scheme; you choose whatever makes sense for your domain:

| URI                        | What it returns                  |
|----------------------------|----------------------------------|
| `config://app`             | Application configuration (JSON) |
| `info://server`            | Server description (plain text)  |
| `users://1/profile`        | Profile for user 1 (JSON)        |

The scheme (`config`, `info`, `users`) is purely descriptive. It helps the AI
understand the *kind* of data at a glance.

## Static resources

A static resource always returns the same URI. Declare one by decorating a
function with `@mcp.resource(uri)`:

```python
@mcp.resource("config://app")
def get_app_config() -> str:
    """Return the application configuration as JSON."""
    config = {"app_name": "MCP Tutorial App", "version": "1.0.0"}
    return json.dumps(config, indent=2)
```

When the client calls `resources/list`, it sees `config://app` in the list.
When it calls `resources/read` with that URI, your function runs and the
result is returned.

## Resource templates

Templates let you expose a *family* of resources whose URI contains a
variable part:

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Return the profile for a given user ID."""
    ...
```

The `{user_id}` placeholder makes this a **template**. It appears under
`resources/templates` rather than `resources/list`. The client fills in the
variable, e.g. `users://42/profile`, and MCP routes the request to your
function with `user_id="42"`.

Templates follow [RFC 6570](https://datatracker.ietf.org/doc/html/rfc6570)
URI Template syntax at the simple-string level.

## MIME types

By default, resources return `text/plain`. You can specify a MIME type when
you know the content is structured:

```python
@mcp.resource("config://app", mime_type="application/json")
def get_app_config() -> str:
    ...
```

This tells the client how to interpret the data. Common types:

| MIME type            | Use case             |
|----------------------|----------------------|
| `text/plain`         | Human-readable text  |
| `application/json`   | Structured data      |
| `text/markdown`      | Documentation        |
| `text/html`          | Rendered content     |

## Resources in this tutorial

| URI / Template               | Type     | Returns                  |
|------------------------------|----------|--------------------------|
| `config://app`               | Static   | App config (JSON)        |
| `info://server`              | Static   | Server info (plain text) |
| `users://{user_id}/profile`  | Template | User profile (JSON)      |

## Running

```bash
# Inspector UI
mcp dev tutorials/03_resources/server.py

# Tests
uv run pytest tutorials/03_resources/ -v
```

## Next steps

You now know tools (actions) and resources (data). Together they give an AI
client the ability to both *read information* and *perform operations* through
your MCP server.
