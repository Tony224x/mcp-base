"""Tests for the Web Fetch MCP Server.

Uses respx to mock HTTP requests and tests internal helper functions directly,
since the MCP server runs as a subprocess and cannot share in-process mocks.
"""

import json

import httpx
import respx

from servers.web_fetch.server import (
    _extract_text,
    _validate_url,
    check_url,
    fetch_json,
    fetch_url,
)

# ── URL validation ──────────────────────────────────────────────────────


def test_validate_url_accepts_http():
    assert _validate_url("http://example.com") is None


def test_validate_url_accepts_https():
    assert _validate_url("https://example.com/path?q=1") is None


def test_validate_url_rejects_ftp():
    error = _validate_url("ftp://example.com/file")
    assert error is not None
    assert "not allowed" in error


def test_validate_url_rejects_file_scheme():
    error = _validate_url("file:///etc/passwd")
    assert error is not None
    assert "not allowed" in error


def test_validate_url_rejects_no_scheme():
    error = _validate_url("not-a-url")
    assert error is not None


# ── HTML text extraction ────────────────────────────────────────────────


def test_extract_text_basic_html():
    html = "<html><body><h1>Title</h1><p>Hello World</p></body></html>"
    text = _extract_text(html)
    assert "Title" in text
    assert "Hello World" in text


def test_extract_text_removes_scripts():
    html = "<html><body><script>alert('xss')</script><p>Content</p></body></html>"
    text = _extract_text(html)
    assert "alert" not in text
    assert "Content" in text


def test_extract_text_removes_styles():
    html = "<html><head><style>body{color:red}</style></head><body><p>Visible</p></body></html>"
    text = _extract_text(html)
    assert "color" not in text
    assert "Visible" in text


# ── fetch_url ───────────────────────────────────────────────────────────


@respx.mock
async def test_fetch_url_extracts_text():
    respx.get("https://example.com/page").mock(
        return_value=httpx.Response(
            200,
            html="<html><body><p>Hello World</p></body></html>",
        )
    )
    result = await fetch_url("https://example.com/page")
    assert "Hello World" in result


@respx.mock
async def test_fetch_url_returns_raw_html():
    respx.get("https://example.com/raw").mock(
        return_value=httpx.Response(
            200,
            html="<html><body><p>Raw HTML</p></body></html>",
        )
    )
    result = await fetch_url("https://example.com/raw", extract_text=False)
    assert "<p>Raw HTML</p>" in result


@respx.mock
async def test_fetch_url_handles_http_error():
    respx.get("https://example.com/404").mock(
        return_value=httpx.Response(404)
    )
    result = await fetch_url("https://example.com/404")
    assert "Error" in result
    assert "404" in result


async def test_fetch_url_rejects_invalid_scheme():
    result = await fetch_url("ftp://example.com/file")
    assert "Error" in result
    assert "not allowed" in result


@respx.mock
async def test_fetch_url_handles_timeout():
    respx.get("https://slow.example.com/").mock(side_effect=httpx.ReadTimeout("timed out"))
    result = await fetch_url("https://slow.example.com/")
    assert "Error" in result
    assert "timed out" in result.lower()


# ── fetch_json ──────────────────────────────────────────────────────────


@respx.mock
async def test_fetch_json_returns_pretty_json():
    payload = {"name": "test", "items": [1, 2, 3]}
    respx.get("https://api.example.com/data").mock(
        return_value=httpx.Response(
            200,
            json=payload,
        )
    )
    result = await fetch_json("https://api.example.com/data")
    parsed = json.loads(result)
    assert parsed == payload
    # Check it is pretty-printed (has indentation)
    assert "\n" in result


@respx.mock
async def test_fetch_json_invalid_json_response():
    respx.get("https://api.example.com/bad").mock(
        return_value=httpx.Response(
            200,
            text="this is not json",
            headers={"content-type": "text/plain"},
        )
    )
    result = await fetch_json("https://api.example.com/bad")
    assert "Error" in result
    assert "not valid JSON" in result


async def test_fetch_json_rejects_invalid_scheme():
    result = await fetch_json("file:///etc/passwd")
    assert "Error" in result


# ── check_url ───────────────────────────────────────────────────────────


@respx.mock
async def test_check_url_returns_status_info():
    respx.head("https://example.com/").mock(
        return_value=httpx.Response(
            200,
            headers={
                "content-type": "text/html; charset=utf-8",
                "content-length": "1234",
            },
        )
    )
    result = await check_url("https://example.com/")
    info = json.loads(result)
    assert info["status_code"] == 200
    assert "text/html" in info["content_type"]
    assert info["content_length"] == "1234"


@respx.mock
async def test_check_url_handles_timeout():
    respx.head("https://slow.example.com/").mock(
        side_effect=httpx.ConnectTimeout("connection timed out")
    )
    result = await check_url("https://slow.example.com/")
    assert "Error" in result
    assert "timed out" in result.lower()


async def test_check_url_rejects_invalid_scheme():
    result = await check_url("ftp://example.com")
    assert "Error" in result


# ── tool listing (via MCP client) ──────────────────────────────────────


async def test_all_tools_are_listed():
    from shared.testing import mcp_client_for

    async with mcp_client_for("servers/web_fetch/server.py") as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        assert names == {"fetch_url", "fetch_json", "check_url"}
