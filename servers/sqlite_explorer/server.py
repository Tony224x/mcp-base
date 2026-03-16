"""SQLite Explorer — MCP server for safe, read-only SQLite database exploration."""

import os
import sqlite3

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SQLiteExplorer")

DB_PATH = os.environ.get("DB_PATH", ".data/explorer.db")

# SQL statements that are NOT allowed (safety: read-only access).
_FORBIDDEN_PREFIXES = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "GRANT",
    "REVOKE",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE",
    "VACUUM",
    "REINDEX",
)


def _get_connection() -> sqlite3.Connection:
    """Create a connection to the configured SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _validate_select(sql: str) -> None:
    """Raise ValueError if the SQL is not a SELECT statement."""
    stripped = sql.strip().upper()
    # Must start with SELECT or WITH (for CTEs)
    if not stripped.startswith("SELECT") and not stripped.startswith("WITH"):
        raise ValueError("Only SELECT queries are allowed.")
    # Extra guard: reject if any forbidden keyword appears as a statement start
    # (handles things like "SELECT 1; DROP TABLE ...")
    for statement in stripped.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        for prefix in _FORBIDDEN_PREFIXES:
            if statement.startswith(prefix):
                raise ValueError(
                    f"Forbidden SQL operation: {prefix}. Only SELECT queries are allowed."
                )


def _format_rows(rows: list[sqlite3.Row]) -> str:
    """Format rows as a readable text table."""
    if not rows:
        return "(no results)"

    keys = rows[0].keys()
    # Calculate column widths
    widths = {k: len(k) for k in keys}
    str_rows = []
    for row in rows:
        str_row = {k: str(row[k]) for k in keys}
        for k in keys:
            widths[k] = max(widths[k], len(str_row[k]))
        str_rows.append(str_row)

    # Build header
    header = " | ".join(k.ljust(widths[k]) for k in keys)
    separator = "-+-".join("-" * widths[k] for k in keys)

    # Build rows
    lines = [header, separator]
    for str_row in str_rows:
        lines.append(" | ".join(str_row[k].ljust(widths[k]) for k in keys))

    return "\n".join(lines)


@mcp.tool()
def query(sql: str) -> str:
    """Execute a SELECT query and return results as a formatted table.

    Only SELECT statements are allowed for safety. INSERT, UPDATE, DELETE,
    DROP, and other modifying statements will be rejected.
    """
    _validate_select(sql)
    conn = _get_connection()
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        return _format_rows(rows)
    finally:
        conn.close()


@mcp.tool()
def list_tables() -> str:
    """List all tables in the database."""
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row["name"] for row in cursor.fetchall()]
        if not tables:
            return "(no tables found)"
        return "\n".join(tables)
    finally:
        conn.close()


@mcp.tool()
def describe_table(table: str) -> str:
    """Show column info for a table (name, type, nullable, primary key)."""
    conn = _get_connection()
    try:
        # Verify the table exists first
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            return f"Table '{table}' not found."

        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        lines = [f"Table: {table}", ""]
        lines.append(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'PK':<5}")
        lines.append(f"{'-' * 20} {'-' * 15} {'-' * 10} {'-' * 5}")
        for col in columns:
            nullable = "NO" if col["notnull"] else "YES"
            pk = "YES" if col["pk"] else ""
            lines.append(f"{col['name']:<20} {(col['type'] or 'ANY'):<15} {nullable:<10} {pk:<5}")
        return "\n".join(lines)
    finally:
        conn.close()


@mcp.resource("db://schema")
def get_schema() -> str:
    """Return the full database schema (all CREATE TABLE statements)."""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL ORDER BY name"
        )
        statements = [row["sql"] for row in cursor.fetchall()]
        if not statements:
            return "(empty database — no tables)"
        return "\n\n".join(statements)
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
