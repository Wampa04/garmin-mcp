"""Garmin MCP tools, grouped by data area.

Each submodule exposes a ``register(mcp)`` function that attaches its tools
to the shared FastMCP instance. ``register_all`` wires up every group.
"""

from __future__ import annotations

from fastmcp import FastMCP

from . import activities, body, daily, heart, recovery

_MODULES = (activities, recovery, heart, daily, body)


def register_all(mcp: FastMCP) -> None:
    """Register every tool group on the given FastMCP instance."""
    for module in _MODULES:
        module.register(mcp)
