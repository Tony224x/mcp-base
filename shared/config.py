"""Configuration helpers for MCP servers."""

import os
from pathlib import Path


def get_env(key: str, default: str | None = None) -> str:
    """Get an environment variable, raising if required and missing."""
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def project_root() -> Path:
    """Return the root of the mcp-base project."""
    return Path(__file__).parent.parent


def data_dir() -> Path:
    """Return the data directory for server storage, creating it if needed."""
    path = project_root() / ".data"
    path.mkdir(exist_ok=True)
    return path
