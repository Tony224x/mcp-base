# mcp-base — Base pédagogique MCP & AI Tools

Apprendre à créer des **MCP servers** (Model Context Protocol) et des **tools pour agents IA**, de zéro à production.

> Dépôt **template** : bouton `Use this template` en haut de page pour partir de ta propre copie.

## Quickstart

```bash
# Installer uv si besoin: https://docs.astral.sh/uv/getting-started/installation/
uv sync --all-extras          # Installer toutes les dépendances
uv run pytest -v              # Vérifier que tout fonctionne
uv run mcp dev tutorials/01_hello_mcp/server.py   # Premier serveur dans l'Inspector
```

## Structure

```
mcp-base/
├── docs/                  Documentation conceptuelle MCP
├── tutorials/             Track progressif (6 niveaux)
│   ├── 01_hello_mcp/      Premier serveur (1 tool echo)
│   ├── 02_tools_deep_dive/ Multiple tools, types, validation
│   ├── 03_resources/       Resources statiques + URI templates
│   ├── 04_prompts/         Prompt templates
│   ├── 05_context_and_errors/ Context, logging, progress, erreurs
│   └── 06_client_basics/   Client MCP, découverte de tools
├── servers/               Serveurs production-ready
│   ├── filesystem/         Read/write/list/search fichiers
│   ├── web_fetch/          Fetch URL, extraction texte
│   ├── sqlite_explorer/    Query SQL, schema resources
│   └── api_bridge/         Bridge API GitHub
├── clients/               Consommer des MCP servers
│   ├── raw_client/         Client MCP SDK brut
│   ├── claude_api/         Bridge MCP → Claude API tool_use
│   └── langchain_agent/    ReAct agent LangChain + MCP
└── shared/                Utilitaires partagés
```

## Parcours d'apprentissage

| Niveau | Module | Concepts |
|--------|--------|----------|
| 1 | `tutorials/01_hello_mcp` | FastMCP, `@mcp.tool()`, `mcp.run()`, stdio |
| 2 | `tutorials/02_tools_deep_dive` | Multiple tools, type hints → JSON Schema, validation |
| 3 | `tutorials/03_resources` | `@mcp.resource()`, URI templates, MIME types |
| 4 | `tutorials/04_prompts` | `@mcp.prompt()`, arguments, messages multi-rôles |
| 5 | `tutorials/05_context_and_errors` | Context (`ctx.info`/`warning`), `report_progress`, erreurs |
| 6 | `tutorials/06_client_basics` | `ClientSession`, `stdio_client`, découverte + appel de tools |

## Commandes utiles

```bash
make install    # uv sync --all-extras
make test       # uv run pytest -v
make lint       # uv run ruff check .
make fmt        # uv run ruff format + check --fix
make run-hello  # Lance le tutorial 01 dans MCP Inspector
```

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)
- Pour les clients Claude API : clé `ANTHROPIC_API_KEY`
- Pour le serveur GitHub : token `GITHUB_TOKEN`
