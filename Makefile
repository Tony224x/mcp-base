.PHONY: install test lint fmt clean

install:
	uv sync --all-extras

test:
	uv run pytest -v

lint:
	uv run ruff check .

fmt:
	uv run ruff format .
	uv run ruff check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ruff_cache dist build *.egg-info

# Tutorial runners
run-hello:
	uv run mcp dev tutorials/01_hello_mcp/server.py

run-tools:
	uv run mcp dev tutorials/02_tools_deep_dive/server.py

run-resources:
	uv run mcp dev tutorials/03_resources/server.py

run-prompts:
	uv run mcp dev tutorials/04_prompts/server.py

run-context:
	uv run mcp dev tutorials/05_context_and_errors/server.py

# Server runners
run-filesystem:
	uv run mcp dev servers/filesystem/server.py

run-web-fetch:
	uv run mcp dev servers/web_fetch/server.py

run-sqlite:
	uv run mcp dev servers/sqlite_explorer/server.py

run-github:
	uv run mcp dev servers/api_bridge/server.py
