# GitHub API Bridge MCP Server

A production-ready MCP server for exploring GitHub repositories, issues, and search results via the GitHub REST API.

## Features

### Tools

| Tool | Description |
|------|-------------|
| `search_repos(query, max_results=5)` | Search GitHub repositories by keyword. |
| `get_repo_info(owner, repo)` | Get detailed repository metadata (stars, forks, language, etc.). |
| `list_issues(owner, repo, state="open", max_results=10)` | List issues for a repository. |
| `get_issue(owner, repo, issue_number)` | Get full details for a specific issue. |

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `GITHUB_TOKEN` | No | Personal access token for higher rate limits. Public endpoints work without it (10 req/min). |

## Usage

```bash
# Run the server (no auth — public access, rate-limited)
uv run python servers/api_bridge/server.py

# Run with a GitHub token for higher rate limits
GITHUB_TOKEN=ghp_xxx uv run python servers/api_bridge/server.py

# Run tests (uses respx to mock HTTP requests)
uv run pytest servers/api_bridge/test_server.py -v
```

## Example

```python
from shared.testing import mcp_client_for

async with mcp_client_for("servers/api_bridge/server.py") as client:
    # Search for repos
    result = await client.call_tool("search_repos", {"query": "fastapi", "max_results": 3})

    # Get repo info
    result = await client.call_tool("get_repo_info", {"owner": "tiangolo", "repo": "fastapi"})

    # List open issues
    result = await client.call_tool("list_issues", {"owner": "tiangolo", "repo": "fastapi"})

    # Get a specific issue
    result = await client.call_tool("get_issue", {"owner": "tiangolo", "repo": "fastapi", "issue_number": 1})
```

## Architecture

The server separates MCP tool definitions from internal async helpers (`_search_repos`, `_get_repo_info`, etc.), making the business logic directly testable with `respx` mocks without needing a MCP subprocess.
