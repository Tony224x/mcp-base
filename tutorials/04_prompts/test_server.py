"""Tests for Tutorial 04 — Prompts."""

from shared.testing import mcp_client_for

SERVER = "tutorials/04_prompts/server.py"


async def test_list_prompts_returns_all_three():
    async with mcp_client_for(SERVER) as client:
        result = await client.list_prompts()
        names = [p.name for p in result.prompts]
        assert "greeting" in names
        assert "code_review" in names
        assert "summarize" in names


async def test_greeting_prompt_contains_name():
    async with mcp_client_for(SERVER) as client:
        result = await client.get_prompt("greeting", {"name": "Alice"})
        assert len(result.messages) >= 1
        assert result.messages[0].role == "user"
        assert "Alice" in result.messages[0].content.text


async def test_code_review_prompt_includes_language_and_code():
    async with mcp_client_for(SERVER) as client:
        result = await client.get_prompt(
            "code_review",
            {"code": "print('hello')", "language": "python"},
        )
        assert len(result.messages) >= 1
        text = result.messages[0].content.text
        assert "python" in text
        assert "print('hello')" in text


async def test_code_review_prompt_defaults_to_python():
    async with mcp_client_for(SERVER) as client:
        result = await client.get_prompt("code_review", {"code": "x = 1"})
        text = result.messages[0].content.text
        assert "python" in text


async def test_summarize_prompt_contains_text_and_style():
    async with mcp_client_for(SERVER) as client:
        result = await client.get_prompt(
            "summarize",
            {"text": "A long document about cats.", "style": "brief"},
        )
        assert len(result.messages) >= 1
        text = result.messages[0].content.text
        assert "brief" in text
        assert "cats" in text


async def test_summarize_prompt_defaults_to_concise():
    async with mcp_client_for(SERVER) as client:
        result = await client.get_prompt(
            "summarize",
            {"text": "Some content here."},
        )
        text = result.messages[0].content.text
        assert "concise" in text
