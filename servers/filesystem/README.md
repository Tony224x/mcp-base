# Filesystem MCP Server

Secure, sandboxed file operations server built with FastMCP.

## Overview

All file operations are restricted to a configurable sandbox root directory, preventing unauthorized access to the host filesystem. Path traversal attempts (`../`) are detected and rejected.

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `MCP_SANDBOX_ROOT` | `.data/sandbox` (project root) | Absolute path to the sandbox directory |

## Tools

| Tool | Description |
|---|---|
| `read_file(path)` | Read file contents (path relative to sandbox) |
| `write_file(path, content)` | Write content to file, creating parent dirs as needed |
| `list_directory(path=".")` | List directory entries with `[DIR]`/`[FILE]` indicators |
| `search_files(pattern, path=".")` | Glob search for files matching a pattern |
| `file_info(path)` | Return JSON metadata (name, type, size, modified date) |

## Security

- All paths are resolved via `pathlib.Path.resolve()` and checked with `is_relative_to()`.
- Path traversal attempts (e.g. `../../etc/passwd`) are rejected with an error.
- The sandbox directory is created automatically if it does not exist.

## Usage

```bash
# Run the server (stdio transport)
uv run python servers/filesystem/server.py

# Run tests
uv run pytest servers/filesystem/test_server.py -v
```
