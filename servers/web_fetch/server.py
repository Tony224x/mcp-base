"""Web Fetch MCP Server — Retrieve URLs and extract content.

Provides tools to fetch web pages, extract clean text from HTML,
retrieve JSON APIs, and check URL availability.
"""

import json
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WebFetch")

_TIMEOUT = 10.0
_ALLOWED_SCHEMES = {"http", "https"}
_MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB


def _validate_url(url: str) -> str | None:
    """Validate a URL and return an error message if invalid, or None if valid."""
    try:
        parsed = urlparse(url)
    except Exception:
        return f"Error: Invalid URL '{url}'."

    if parsed.scheme not in _ALLOWED_SCHEMES:
        return (
            f"Error: URL scheme '{parsed.scheme}' is not allowed. "
            f"Only {', '.join(sorted(_ALLOWED_SCHEMES))} are supported."
        )

    if not parsed.hostname:
        return f"Error: URL '{url}' has no hostname."

    return None


def _extract_text(html: str) -> str:
    """Parse HTML and return clean, readable text."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned


async def _do_fetch(url: str, method: str = "GET", follow_redirects: bool = True) -> httpx.Response:
    """Perform an HTTP request with standard settings."""
    async with httpx.AsyncClient(
        timeout=_TIMEOUT,
        follow_redirects=follow_redirects,
        headers={"User-Agent": "MCP-WebFetch/1.0"},
    ) as client:
        return await client.request(method, url)


@mcp.tool()
async def fetch_url(url: str, extract_text: bool = True) -> str:
    """Fetch a URL and return its content.

    Args:
        url: The URL to fetch (http/https only).
        extract_text: If True, parse HTML and return clean text.
                      If False, return the raw HTML.

    Returns:
        The page content as clean text or raw HTML.
    """
    error = _validate_url(url)
    if error:
        return error

    try:
        response = await _do_fetch(url)
        response.raise_for_status()
    except httpx.TimeoutException:
        return f"Error: Request to '{url}' timed out after {_TIMEOUT}s."
    except httpx.HTTPStatusError as exc:
        return f"Error: HTTP {exc.response.status_code} for '{url}'."
    except httpx.RequestError as exc:
        return f"Error: Failed to fetch '{url}': {exc}"

    content = response.text
    if extract_text:
        return _extract_text(content)
    return content


@mcp.tool()
async def fetch_json(url: str) -> str:
    """Fetch a URL and return pretty-printed JSON.

    Args:
        url: The URL to fetch (http/https only). Must return valid JSON.

    Returns:
        Pretty-printed JSON string.
    """
    error = _validate_url(url)
    if error:
        return error

    try:
        response = await _do_fetch(url)
        response.raise_for_status()
    except httpx.TimeoutException:
        return f"Error: Request to '{url}' timed out after {_TIMEOUT}s."
    except httpx.HTTPStatusError as exc:
        return f"Error: HTTP {exc.response.status_code} for '{url}'."
    except httpx.RequestError as exc:
        return f"Error: Failed to fetch '{url}': {exc}"

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        return f"Error: Response from '{url}' is not valid JSON."

    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
async def check_url(url: str) -> str:
    """Check URL availability with a HEAD request.

    Args:
        url: The URL to check (http/https only).

    Returns:
        JSON with status_code, content_type, and content_length headers.
    """
    error = _validate_url(url)
    if error:
        return error

    try:
        response = await _do_fetch(url, method="HEAD")
    except httpx.TimeoutException:
        return f"Error: Request to '{url}' timed out after {_TIMEOUT}s."
    except httpx.RequestError as exc:
        return f"Error: Failed to reach '{url}': {exc}"

    info = {
        "url": str(response.url),
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", "unknown"),
        "content_length": response.headers.get("content-length", "unknown"),
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    mcp.run()
