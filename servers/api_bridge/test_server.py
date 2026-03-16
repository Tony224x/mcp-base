"""Tests for the GitHub API Bridge MCP server.

Uses respx to mock HTTP requests to the GitHub API, testing the internal
helper functions directly (no subprocess needed for mocking).
"""

import httpx
import pytest
import respx

# ── Fixtures: mock data ─────────────────────────────────────────────────

MOCK_SEARCH_RESPONSE = {
    "total_count": 2,
    "items": [
        {
            "full_name": "pallets/flask",
            "description": "The Python Micro Framework",
            "stargazers_count": 65000,
            "language": "Python",
        },
        {
            "full_name": "django/django",
            "description": "The Web framework for perfectionists",
            "stargazers_count": 75000,
            "language": "Python",
        },
    ],
}

MOCK_REPO_RESPONSE = {
    "full_name": "pallets/flask",
    "description": "The Python Micro Framework",
    "language": "Python",
    "stargazers_count": 65000,
    "forks_count": 16000,
    "open_issues_count": 5,
    "created_at": "2010-04-06T11:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z",
    "html_url": "https://github.com/pallets/flask",
}

MOCK_ISSUES_RESPONSE = [
    {
        "number": 42,
        "title": "Bug in routing",
        "state": "open",
        "labels": [{"name": "bug"}],
        "user": {"login": "alice"},
    },
    {
        "number": 43,
        "title": "Feature request: async support",
        "state": "open",
        "labels": [{"name": "enhancement"}, {"name": "discussion"}],
        "user": {"login": "bob"},
    },
]

MOCK_ISSUE_DETAIL = {
    "number": 42,
    "title": "Bug in routing",
    "state": "open",
    "user": {"login": "alice"},
    "labels": [{"name": "bug"}],
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-12T15:30:00Z",
    "comments": 3,
    "body": "When I try to register a route with special characters, it fails.",
}


# ── Tests: search_repos ─────────────────────────────────────────────────


@respx.mock
async def test_search_repos():
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=MOCK_SEARCH_RESPONSE)
    )
    from servers.api_bridge.server import _search_repos

    result = await _search_repos("flask", 5)
    assert "pallets/flask" in result
    assert "django/django" in result
    assert "65000" in result
    assert "Python" in result


@respx.mock
async def test_search_repos_no_results():
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"total_count": 0, "items": []})
    )
    from servers.api_bridge.server import _search_repos

    result = await _search_repos("xyznonexistentrepo123456", 5)
    assert "No repositories found" in result


# ── Tests: get_repo_info ────────────────────────────────────────────────


@respx.mock
async def test_get_repo_info():
    respx.get("https://api.github.com/repos/pallets/flask").mock(
        return_value=httpx.Response(200, json=MOCK_REPO_RESPONSE)
    )
    from servers.api_bridge.server import _get_repo_info

    result = await _get_repo_info("pallets", "flask")
    assert "pallets/flask" in result
    assert "65000" in result
    assert "16000" in result
    assert "Python" in result
    assert "The Python Micro Framework" in result


@respx.mock
async def test_get_repo_info_not_found():
    respx.get("https://api.github.com/repos/nonexistent/repo404").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )
    from servers.api_bridge.server import _get_repo_info

    with pytest.raises(httpx.HTTPStatusError):
        await _get_repo_info("nonexistent", "repo404")


# ── Tests: list_issues ──────────────────────────────────────────────────


@respx.mock
async def test_list_issues():
    respx.get("https://api.github.com/repos/pallets/flask/issues").mock(
        return_value=httpx.Response(200, json=MOCK_ISSUES_RESPONSE)
    )
    from servers.api_bridge.server import _list_issues

    result = await _list_issues("pallets", "flask")
    assert "#42" in result
    assert "Bug in routing" in result
    assert "#43" in result
    assert "async support" in result
    assert "bug" in result


@respx.mock
async def test_list_issues_empty():
    respx.get("https://api.github.com/repos/pallets/flask/issues").mock(
        return_value=httpx.Response(200, json=[])
    )
    from servers.api_bridge.server import _list_issues

    result = await _list_issues("pallets", "flask")
    assert "No open issues" in result


# ── Tests: get_issue ────────────────────────────────────────────────────


@respx.mock
async def test_get_issue():
    respx.get("https://api.github.com/repos/pallets/flask/issues/42").mock(
        return_value=httpx.Response(200, json=MOCK_ISSUE_DETAIL)
    )
    from servers.api_bridge.server import _get_issue

    result = await _get_issue("pallets", "flask", 42)
    assert "Bug in routing" in result
    assert "#42" in result
    assert "alice" in result
    assert "special characters" in result
    assert "bug" in result


@respx.mock
async def test_get_issue_not_found():
    respx.get("https://api.github.com/repos/pallets/flask/issues/99999").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )
    from servers.api_bridge.server import _get_issue

    with pytest.raises(httpx.HTTPStatusError):
        await _get_issue("pallets", "flask", 99999)
