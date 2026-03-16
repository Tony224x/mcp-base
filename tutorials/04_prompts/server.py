"""Tutorial 04 — Prompts: Reusable prompt templates for LLMs."""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("PromptServer")


@mcp.prompt()
def greeting(name: str) -> str:
    """Generate a warm greeting for a user."""
    return f"Greet the user named {name} warmly"


@mcp.prompt()
def code_review(code: str, language: str = "python") -> list[base.Message]:
    """Review code in a given programming language."""
    return [
        base.UserMessage(
            content=f"Please review the following {language} code for correctness, "
            f"style, and potential improvements:\n\n```{language}\n{code}\n```"
        ),
    ]


@mcp.prompt()
def summarize(text: str, style: str = "concise") -> str:
    """Summarize text in a given style."""
    return f"Summarize the following text in a {style} style:\n\n{text}"


if __name__ == "__main__":
    mcp.run()
