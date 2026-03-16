"""Tests for the Filesystem MCP Server."""

import json
import os

from shared.testing import mcp_client_for

SERVER = "servers/filesystem/server.py"


def _env(tmp_path) -> dict[str, str]:
    """Build env dict with MCP_SANDBOX_ROOT pointing to tmp_path."""
    return {**os.environ, "MCP_SANDBOX_ROOT": str(tmp_path)}


# ── read_file / write_file ──────────────────────────────────────────────


async def test_write_and_read_file(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        write_result = await client.call_tool(
            "write_file", {"path": "hello.txt", "content": "Hello, sandbox!"}
        )
        assert "Successfully wrote" in write_result.content[0].text

        read_result = await client.call_tool("read_file", {"path": "hello.txt"})
        assert read_result.content[0].text == "Hello, sandbox!"


async def test_write_creates_parent_dirs(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        await client.call_tool(
            "write_file", {"path": "sub/dir/deep.txt", "content": "nested"}
        )
        result = await client.call_tool("read_file", {"path": "sub/dir/deep.txt"})
        assert result.content[0].text == "nested"


async def test_read_nonexistent_file(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("read_file", {"path": "missing.txt"})
        assert "Error" in result.content[0].text


# ── list_directory ──────────────────────────────────────────────────────


async def test_list_directory(tmp_path):
    # Pre-populate sandbox
    (tmp_path / "afile.txt").write_text("a")
    (tmp_path / "subdir").mkdir()

    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("list_directory", {"path": "."})
        text = result.content[0].text
        assert "[DIR]" in text
        assert "subdir" in text
        assert "[FILE]" in text
        assert "afile.txt" in text


async def test_list_empty_directory(tmp_path):
    (tmp_path / "empty").mkdir()
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("list_directory", {"path": "empty"})
        assert result.content[0].text == "(empty directory)"


# ── search_files ────────────────────────────────────────────────────────


async def test_search_files_glob(tmp_path):
    (tmp_path / "readme.md").write_text("# Hi")
    (tmp_path / "notes.txt").write_text("notes")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "data.txt").write_text("data")

    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("search_files", {"pattern": "**/*.txt"})
        text = result.content[0].text
        assert "notes.txt" in text
        assert "data.txt" in text
        assert "readme.md" not in text


async def test_search_files_no_match(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("search_files", {"pattern": "*.xyz"})
        assert "No files matching" in result.content[0].text


# ── file_info ───────────────────────────────────────────────────────────


async def test_file_info(tmp_path):
    (tmp_path / "sample.txt").write_text("hello world")

    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("file_info", {"path": "sample.txt"})
        info = json.loads(result.content[0].text)
        assert info["name"] == "sample.txt"
        assert info["type"] == "file"
        assert info["size"] == 11
        assert "modified" in info


async def test_file_info_directory(tmp_path):
    (tmp_path / "mydir").mkdir()

    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("file_info", {"path": "mydir"})
        info = json.loads(result.content[0].text)
        assert info["type"] == "directory"


async def test_file_info_nonexistent(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("file_info", {"path": "ghost.txt"})
        assert "Error" in result.content[0].text


# ── Security: path traversal rejection ──────────────────────────────────


async def test_path_traversal_rejected(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool("read_file", {"path": "../../etc/passwd"})
        text = result.content[0].text
        assert "error" in text.lower() or "denied" in text.lower()


async def test_path_traversal_write_rejected(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        result = await client.call_tool(
            "write_file", {"path": "../../../tmp/evil.txt", "content": "bad"}
        )
        text = result.content[0].text
        assert "error" in text.lower() or "denied" in text.lower()


# ── tool listing ────────────────────────────────────────────────────────


async def test_all_tools_are_listed(tmp_path):
    async with mcp_client_for(SERVER, env=_env(tmp_path)) as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        assert names == {"read_file", "write_file", "list_directory", "search_files", "file_info"}
