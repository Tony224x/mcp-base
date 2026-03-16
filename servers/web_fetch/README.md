# Web Fetch MCP Server

Web content retrieval server built with FastMCP. Fetches URLs, extracts clean text from HTML, retrieves JSON APIs, and checks URL availability.

## Overview

Provides safe HTTP fetching with URL scheme validation, configurable timeouts, and HTML-to-text extraction powered by BeautifulSoup.

## Dependencies

Requires the `web` optional dependencies:

```bash
uv sync --extra web --extra dev
```

## Tools

| Tool | Description |
|---|---|
| `fetch_url(url, extract_text=True)` | Fetch a URL; optionally extract clean text from HTML |
| `fetch_json(url)` | Fetch a URL and return pretty-printed JSON |
| `check_url(url)` | HEAD request returning status code and headers info |

## Security

- Only `http` and `https` URL schemes are allowed.
- Requests time out after 10 seconds.
- Scripts and style tags are stripped during text extraction.

## Usage

```bash
# Run the server (stdio transport)
uv run python servers/web_fetch/server.py

# Run tests
uv run pytest servers/web_fetch/test_server.py -v
```
