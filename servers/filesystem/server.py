"""Filesystem MCP Server — Secure, sandboxed file operations.

All file operations are restricted to a configurable sandbox root directory.
Set the MCP_SANDBOX_ROOT environment variable to override the default
(.data/sandbox under the project root).
"""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from shared.config import data_dir

mcp = FastMCP("Filesystem")


def _sandbox_root() -> Path:
    """Return the sandbox root directory, creating it if needed."""
    env_root = os.environ.get("MCP_SANDBOX_ROOT")
    if env_root:
        root = Path(env_root)
    else:
        root = data_dir() / "sandbox"
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _safe_resolve(path: str) -> Path:
    """Resolve a user-supplied path within the sandbox, rejecting traversals.

    Raises:
        ValueError: If the resolved path escapes the sandbox root.
    """
    root = _sandbox_root()
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path '{path}' escapes the sandbox root. Access denied.")
    return resolved


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file. Path is relative to the sandbox root."""
    target = _safe_resolve(path)
    if not target.is_file():
        return f"Error: '{path}' is not a file or does not exist."
    return target.read_text(encoding="utf-8")


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories as needed.

    Path is relative to the sandbox root. Returns a confirmation message.
    """
    target = _safe_resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} bytes to '{path}'."


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of a directory with [DIR] and [FILE] indicators.

    Path is relative to the sandbox root. Defaults to the root itself.
    """
    target = _safe_resolve(path)
    if not target.is_dir():
        return f"Error: '{path}' is not a directory or does not exist."

    entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    lines = []
    for entry in entries:
        indicator = "[DIR] " if entry.is_dir() else "[FILE]"
        lines.append(f"{indicator} {entry.name}")

    if not lines:
        return "(empty directory)"
    return "\n".join(lines)


@mcp.tool()
def search_files(pattern: str, path: str = ".") -> str:
    """Search for files matching a glob pattern within the sandbox.

    Args:
        pattern: Glob pattern (e.g. "*.txt", "**/*.py").
        path: Starting directory relative to the sandbox root. Defaults to root.

    Returns:
        Newline-separated list of matching file paths (relative to sandbox root).
    """
    root = _sandbox_root()
    target = _safe_resolve(path)
    if not target.is_dir():
        return f"Error: '{path}' is not a directory or does not exist."

    matches = []
    for match in sorted(target.glob(pattern)):
        if match.is_file():
            try:
                rel = match.relative_to(root)
                matches.append(str(rel))
            except ValueError:
                continue

    if not matches:
        return f"No files matching '{pattern}' found."
    return "\n".join(matches)


@mcp.tool()
def file_info(path: str) -> str:
    """Return metadata about a file or directory.

    Returns JSON with: name, type, size (bytes), modified (ISO timestamp).
    Path is relative to the sandbox root.
    """
    target = _safe_resolve(path)
    if not target.exists():
        return f"Error: '{path}' does not exist."

    stat = target.stat()
    modified_dt = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

    info = {
        "name": target.name,
        "type": "directory" if target.is_dir() else "file",
        "size": stat.st_size,
        "modified": modified_dt.isoformat(),
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    mcp.run()
