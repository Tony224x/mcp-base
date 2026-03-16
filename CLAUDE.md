# mcp-base — Instructions pour Claude Code

## Projet

Base pédagogique MCP (Model Context Protocol) : tutoriels progressifs + serveurs production-ready.

## Stack

- Python 3.12, gestionnaire de paquets: `uv`
- SDK: `mcp[cli]>=1.8.0` (FastMCP)
- Tests: `pytest` + `pytest-asyncio` (mode auto)
- Lint: `ruff`

## Commandes

```bash
uv sync --all-extras     # Installer toutes les dépendances
uv run pytest -v          # Lancer tous les tests
uv run ruff check .       # Lint
uv run ruff format .      # Format
```

## Conventions

- Chaque module (tutorial/server/client) a son propre `README.md`, `server.py` ou `client.py`, et `test_*.py`
- Les tests utilisent le helper `shared.testing.mcp_client_for()` pour tester les serveurs MCP
- Les serveurs MCP utilisent FastMCP (décorateurs `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`)
- asyncio_mode = "auto" dans pytest : les tests async n'ont pas besoin du décorateur `@pytest.mark.asyncio`
- Ne pas écrire sur stdout/stderr dans les serveurs MCP (ça corrompt le flux JSON-RPC stdio)

## Structure

- `tutorials/` : 6 niveaux progressifs (01 à 06)
- `servers/` : serveurs production (filesystem, web_fetch, sqlite_explorer, api_bridge)
- `clients/` : consommer des serveurs MCP (raw_client, claude_api, langchain_agent)
- `shared/` : utilitaires partagés (logging, config, testing)
- `docs/` : documentation conceptuelle MCP
