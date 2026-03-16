"""Tests for Tutorial 02 — Tools Deep Dive."""

import json

from shared.testing import mcp_client_for

SERVER = "tutorials/02_tools_deep_dive/server.py"


# ── add ──────────────────────────────────────────────────────────────────

async def test_add_positive_numbers():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        assert result.content[0].text == "5"


async def test_add_negative_numbers():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("add", {"a": -10, "b": 4})
        assert result.content[0].text == "-6"


async def test_add_zeros():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("add", {"a": 0, "b": 0})
        assert result.content[0].text == "0"


# ── calculate_bmi ────────────────────────────────────────────────────────

async def test_bmi_normal_weight():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("calculate_bmi", {"weight_kg": 70, "height_m": 1.75})
        text = result.content[0].text
        assert "22.9" in text
        assert "normal weight" in text


async def test_bmi_underweight():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("calculate_bmi", {"weight_kg": 50, "height_m": 1.80})
        text = result.content[0].text
        assert "underweight" in text


async def test_bmi_invalid_height():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("calculate_bmi", {"weight_kg": 70, "height_m": 0})
        assert "error" in result.content[0].text.lower()


# ── count_words ──────────────────────────────────────────────────────────

async def test_count_words_simple():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("count_words", {"text": "hello world"})
        data = json.loads(result.content[0].text)
        assert data["word_count"] == 2
        assert data["char_count"] == 11
        assert data["line_count"] == 1


async def test_count_words_multiline():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("count_words", {"text": "line one\nline two\nline three"})
        data = json.loads(result.content[0].text)
        assert data["word_count"] == 6
        assert data["line_count"] == 3


async def test_count_words_empty():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("count_words", {"text": ""})
        data = json.loads(result.content[0].text)
        assert data["word_count"] == 0
        assert data["char_count"] == 0
        assert data["line_count"] == 0


# ── format_list ──────────────────────────────────────────────────────────

async def test_format_list_bullets():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("format_list", {"items": ["a", "b", "c"]})
        text = result.content[0].text
        assert text == "- a\n- b\n- c"


async def test_format_list_numbered():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("format_list", {"items": ["x", "y"], "numbered": True})
        text = result.content[0].text
        assert text == "1. x\n2. y"


async def test_format_list_empty():
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("format_list", {"items": []})
        assert result.content[0].text == "(empty list)"


async def test_format_list_default_not_numbered():
    """Verify that numbered defaults to False (bullet style)."""
    async with mcp_client_for(SERVER) as client:
        result = await client.call_tool("format_list", {"items": ["only"]})
        assert result.content[0].text.startswith("- ")


# ── tool listing ─────────────────────────────────────────────────────────

async def test_all_tools_are_listed():
    async with mcp_client_for(SERVER) as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        assert names == {"add", "calculate_bmi", "count_words", "format_list"}
