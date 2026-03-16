"""Logging configuration for MCP servers.

MCP servers communicate over stdio, so we must NOT write logs to stdout/stderr
during normal operation (it would corrupt the JSON-RPC stream).
Instead, we use the MCP context's built-in logging (ctx.info, ctx.warning, etc.)
inside tool handlers, and file-based logging for server-level diagnostics.
"""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / ".logs"


def setup_file_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Create a file-based logger for server diagnostics.

    Use this for debugging outside of tool handlers.
    Inside tool handlers, prefer ctx.info() / ctx.warning() instead.
    """
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.FileHandler(LOG_DIR / f"{name}.log")
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)

    return logger
