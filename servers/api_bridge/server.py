"""GitHub API Bridge — MCP server for exploring GitHub via the REST API."""

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GitHubBridge")

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    """Build request headers, including auth token if available."""
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "mcp-base"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


async def _github_get(path: str, params: dict | None = None) -> dict | list:
    """Perform a GET request against the GitHub API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}{path}", headers=_headers(), params=params, timeout=10
        )
        resp.raise_for_status()
        return resp.json()


# ── Internal helpers (testable without MCP subprocess) ───────────────────


async def _search_repos(query: str, max_results: int = 5) -> str:
    """Search GitHub repositories and return a formatted summary."""
    data = await _github_get("/search/repositories", params={"q": query, "per_page": max_results})
    items = data.get("items", [])
    if not items:
        return f"No repositories found for query: {query}"

    lines = []
    for repo in items:
        stars = repo.get("stargazers_count", 0)
        lang = repo.get("language") or "N/A"
        desc = repo.get("description") or "(no description)"
        lines.append(f"  {repo['full_name']}  {stars} stars  [{lang}]")
        lines.append(f"    {desc}")
    return "\n".join(lines)


async def _get_repo_info(owner: str, repo: str) -> str:
    """Get detailed info for a single repository."""
    data = await _github_get(f"/repos/{owner}/{repo}")
    lines = [
        f"Repository: {data['full_name']}",
        f"Description: {data.get('description') or '(none)'}",
        f"Language: {data.get('language') or 'N/A'}",
        f"Stars: {data.get('stargazers_count', 0)}",
        f"Forks: {data.get('forks_count', 0)}",
        f"Open Issues: {data.get('open_issues_count', 0)}",
        f"Created: {data.get('created_at', 'N/A')}",
        f"Updated: {data.get('updated_at', 'N/A')}",
        f"URL: {data.get('html_url', 'N/A')}",
    ]
    return "\n".join(lines)


async def _list_issues(owner: str, repo: str, state: str = "open", max_results: int = 10) -> str:
    """List issues for a repository."""
    data = await _github_get(
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": max_results},
    )
    if not data:
        return f"No {state} issues found for {owner}/{repo}."

    lines = []
    for issue in data:
        labels = ", ".join(lbl["name"] for lbl in issue.get("labels", []))
        label_str = f"  [{labels}]" if labels else ""
        lines.append(f"  #{issue['number']} {issue['title']}{label_str}")
    return f"Issues for {owner}/{repo} (state={state}):\n" + "\n".join(lines)


async def _get_issue(owner: str, repo: str, issue_number: int) -> str:
    """Get details for a specific issue."""
    data = await _github_get(f"/repos/{owner}/{repo}/issues/{issue_number}")
    labels = ", ".join(lbl["name"] for lbl in data.get("labels", []))
    lines = [
        f"Issue #{data['number']}: {data['title']}",
        f"State: {data['state']}",
        f"Author: {data['user']['login']}",
        f"Labels: {labels or '(none)'}",
        f"Created: {data.get('created_at', 'N/A')}",
        f"Updated: {data.get('updated_at', 'N/A')}",
        f"Comments: {data.get('comments', 0)}",
        "",
        data.get("body") or "(no body)",
    ]
    return "\n".join(lines)


# ── MCP tool definitions ────────────────────────────────────────────────


@mcp.tool()
async def search_repos(query: str, max_results: int = 5) -> str:
    """Search GitHub repositories via the public API.

    Returns a formatted list of matching repos with stars, language, and description.
    No authentication required (rate-limited to 10 req/min without a token).
    """
    return await _search_repos(query, max_results)


@mcp.tool()
async def get_repo_info(owner: str, repo: str) -> str:
    """Get detailed information about a GitHub repository.

    Returns stars, forks, description, language, and other metadata.
    """
    return await _get_repo_info(owner, repo)


@mcp.tool()
async def list_issues(owner: str, repo: str, state: str = "open", max_results: int = 10) -> str:
    """List issues for a GitHub repository.

    Args:
        owner: Repository owner (user or org).
        repo: Repository name.
        state: Filter by state — "open", "closed", or "all".
        max_results: Maximum number of issues to return (default 10).
    """
    return await _list_issues(owner, repo, state, max_results)


@mcp.tool()
async def get_issue(owner: str, repo: str, issue_number: int) -> str:
    """Get detailed information about a specific GitHub issue.

    Returns title, state, author, labels, body, and other metadata.
    """
    return await _get_issue(owner, repo, issue_number)


if __name__ == "__main__":
    mcp.run()
