# Tutorials — Parcours d'apprentissage MCP

Progression de zéro à la maîtrise de MCP en 6 niveaux.

## Prérequis

```bash
uv sync --all-extras   # Depuis la racine du projet
```

## Parcours

### Niveau 1 — [Hello MCP](./01_hello_mcp/)
Premier serveur MCP : un seul tool `echo`. Concepts : `FastMCP`, `@mcp.tool()`, `mcp.run()`, transport stdio.

### Niveau 2 — [Tools Deep Dive](./02_tools_deep_dive/)
Multiple tools avec types Python riches. Concepts : type hints → JSON Schema automatique, validation des entrées, gestion d'erreurs.

### Niveau 3 — [Resources](./03_resources/)
Exposer des données en lecture seule via des Resources. Concepts : `@mcp.resource()`, URI templates, MIME types.

### Niveau 4 — [Prompts](./04_prompts/)
Templates de prompts réutilisables. Concepts : `@mcp.prompt()`, arguments, messages multi-rôles.

### Niveau 5 — [Context & Errors](./05_context_and_errors/)
Communication serveur→client et gestion d'erreurs robuste. Concepts : `ctx.info()`, `ctx.warning()`, `report_progress()`, erreurs structurées.

### Niveau 6 — [Client Basics](./06_client_basics/)
Écrire un client MCP qui découvre et appelle des tools. Concepts : `ClientSession`, `stdio_client`, discovery, appel de tools.

## Tester un tutorial

```bash
# Tests automatisés
uv run pytest tutorials/01_hello_mcp/ -v

# Inspection interactive (ouvre le MCP Inspector dans le navigateur)
uv run mcp dev tutorials/01_hello_mcp/server.py
```
