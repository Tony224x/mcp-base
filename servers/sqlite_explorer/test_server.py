"""Tests for the SQLite Explorer MCP server."""

import os
import sqlite3

import pytest

from shared.testing import mcp_client_for

SERVER = "servers/sqlite_explorer/server.py"


@pytest.fixture
def db_path(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
    conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT)")
    conn.execute("INSERT INTO posts VALUES (1, 1, 'Hello World')")
    conn.commit()
    conn.close()
    return db


def _env(db_path) -> dict:
    return {**os.environ, "DB_PATH": str(db_path)}


# ── list_tables ──────────────────────────────────────────────────────────


async def test_list_tables(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("list_tables", {})
        text = result.content[0].text
        assert "users" in text
        assert "posts" in text


# ── describe_table ───────────────────────────────────────────────────────


async def test_describe_table(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("describe_table", {"table": "users"})
        text = result.content[0].text
        assert "id" in text
        assert "name" in text
        assert "email" in text
        assert "INTEGER" in text
        assert "TEXT" in text


async def test_describe_table_not_found(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("describe_table", {"table": "nonexistent"})
        text = result.content[0].text
        assert "not found" in text.lower()


# ── query (SELECT) ──────────────────────────────────────────────────────


async def test_query_select(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool(
            "query", {"sql": "SELECT name, email FROM users ORDER BY id"}
        )
        text = result.content[0].text
        assert "Alice" in text
        assert "Bob" in text
        assert "alice@example.com" in text


async def test_query_with_where(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("query", {"sql": "SELECT name FROM users WHERE id = 1"})
        text = result.content[0].text
        assert "Alice" in text
        assert "Bob" not in text


# ── query rejection (non-SELECT) ────────────────────────────────────────


async def test_query_rejects_insert(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool(
            "query", {"sql": "INSERT INTO users VALUES (3, 'Eve', 'eve@example.com')"}
        )
        assert result.isError or "only select" in result.content[0].text.lower()


async def test_query_rejects_drop(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("query", {"sql": "DROP TABLE users"})
        assert result.isError or "only select" in result.content[0].text.lower()


async def test_query_rejects_delete(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("query", {"sql": "DELETE FROM users WHERE id = 1"})
        assert result.isError or "only select" in result.content[0].text.lower()


async def test_query_rejects_update(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool(
            "query", {"sql": "UPDATE users SET name = 'Evil' WHERE id = 1"}
        )
        assert result.isError or "only select" in result.content[0].text.lower()


# ── empty results ────────────────────────────────────────────────────────


async def test_query_empty_results(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.call_tool("query", {"sql": "SELECT * FROM users WHERE id = 999"})
        text = result.content[0].text
        assert "no results" in text.lower()


# ── schema resource ─────────────────────────────────────────────────────


async def test_read_schema_resource(db_path):
    async with mcp_client_for(SERVER, env=_env(db_path)) as client:
        result = await client.read_resource("db://schema")
        text = result.contents[0].text
        assert "CREATE TABLE" in text
        assert "users" in text
        assert "posts" in text
