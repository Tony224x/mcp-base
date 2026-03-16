# SQLite Explorer MCP Server

A production-ready MCP server for safe, read-only exploration of SQLite databases.

## Features

### Tools

| Tool | Description |
|------|-------------|
| `query(sql)` | Execute a SELECT query and return results as a formatted table. Non-SELECT statements are rejected for safety. |
| `list_tables()` | List all tables in the database. |
| `describe_table(table)` | Show column info (name, type, nullable, primary key) for a table. |

### Resources

| URI | Description |
|-----|-------------|
| `db://schema` | Full database schema (all CREATE TABLE statements). |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DB_PATH` | `.data/explorer.db` | Path to the SQLite database file. |

## Safety

The `query` tool only allows `SELECT` (and `WITH` for CTEs) statements. All modifying operations — `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc. — are rejected before execution.

## Usage

```bash
# Run the server
DB_PATH=my_database.db uv run python servers/sqlite_explorer/server.py

# Run tests
uv run pytest servers/sqlite_explorer/test_server.py -v
```

## Example

```python
from shared.testing import mcp_client_for

async with mcp_client_for("servers/sqlite_explorer/server.py", env={"DB_PATH": "my.db"}) as client:
    # List tables
    tables = await client.call_tool("list_tables", {})

    # Describe a table
    info = await client.call_tool("describe_table", {"table": "users"})

    # Run a query
    result = await client.call_tool("query", {"sql": "SELECT * FROM users LIMIT 10"})

    # Read the full schema
    schema = await client.read_resource("db://schema")
```
