# Tutorial 04 — Prompts

## What are Prompts in MCP?

Prompts are **reusable prompt templates** that an MCP server exposes to clients and LLMs. They allow a server to define parameterized instructions that clients can discover, fill in with arguments, and send to a language model.

Think of prompts as pre-built recipes: the server defines the structure and wording, and the client fills in the blanks.

## Key Concepts

### Single-Message Prompts

The simplest prompt returns a single string. FastMCP wraps it into a user message automatically:

```python
@mcp.prompt()
def greeting(name: str) -> str:
    """Generate a warm greeting for a user."""
    return f"Greet the user named {name} warmly"
```

### Multi-Message Prompts

For more complex interactions, return a list of `Message` objects. This lets you define multi-turn conversations or system/user/assistant message sequences:

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt()
def code_review(code: str, language: str = "python") -> list[base.Message]:
    """Review code in a given programming language."""
    return [
        base.UserMessage(
            content=f"Review this {language} code:\n\n```{language}\n{code}\n```"
        ),
    ]
```

### Arguments with Defaults

Prompt arguments work like Python function parameters. Required arguments must be provided; optional arguments have defaults:

```python
@mcp.prompt()
def summarize(text: str, style: str = "concise") -> str:
    return f"Summarize in a {style} style:\n\n{text}"
```

## Client Workflow

1. **Discover** — `client.list_prompts()` returns all available prompts with their names, descriptions, and argument schemas.
2. **Fill in** — The client (or user) provides the required arguments.
3. **Retrieve** — `client.get_prompt(name, arguments)` returns the rendered messages ready to be sent to an LLM.

## Running

```bash
# Interactive inspection
uv run mcp dev tutorials/04_prompts/server.py

# Automated tests
uv run pytest tutorials/04_prompts/ -v
```
