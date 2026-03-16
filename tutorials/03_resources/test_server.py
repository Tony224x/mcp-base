"""Tests for Tutorial 03 — Resources."""

import json

from shared.testing import mcp_client_for

SERVER = "tutorials/03_resources/server.py"


# ── Static resource: config://app ────────────────────────────────────────

async def test_read_app_config():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("config://app")
        config = json.loads(result.contents[0].text)
        assert config["app_name"] == "MCP Tutorial App"
        assert config["version"] == "1.0.0"
        assert "tools" in config["features"]


async def test_app_config_has_expected_keys():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("config://app")
        config = json.loads(result.contents[0].text)
        expected_keys = {"app_name", "version", "debug", "max_connections", "features"}
        assert expected_keys == set(config.keys())


# ── Static resource: info://server ───────────────────────────────────────

async def test_read_server_info():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("info://server")
        text = result.contents[0].text
        assert "Resources Tutorial Server" in text
        assert "mcp-base" in text


# ── Resource template: users://{user_id}/profile ─────────────────────────

async def test_read_user_profile_alice():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("users://1/profile")
        profile = json.loads(result.contents[0].text)
        assert profile["name"] == "Alice"
        assert profile["role"] == "admin"
        assert profile["user_id"] == "1"


async def test_read_user_profile_bob():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("users://2/profile")
        profile = json.loads(result.contents[0].text)
        assert profile["name"] == "Bob"
        assert profile["email"] == "bob@example.com"


async def test_read_unknown_user():
    async with mcp_client_for(SERVER) as client:
        result = await client.read_resource("users://999/profile")
        data = json.loads(result.contents[0].text)
        assert "error" in data
        assert "999" in data["error"]


# ── Listing resources ────────────────────────────────────────────────────

async def test_list_static_resources():
    async with mcp_client_for(SERVER) as client:
        result = await client.list_resources()
        uris = [str(r.uri) for r in result.resources]
        assert "config://app" in uris
        assert "info://server" in uris


async def test_list_resource_templates():
    async with mcp_client_for(SERVER) as client:
        result = await client.list_resource_templates()
        template_uris = [t.uriTemplate for t in result.resourceTemplates]
        assert any("user_id" in uri for uri in template_uris)
