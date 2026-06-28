"""Garmin Connect MCP server.

Exposes 17 read-only tools over Garmin Connect data via the MCP HTTP
transport, protected by a static bearer token. Designed to run as a Docker
container behind Traefik and be added as a Custom Connector in Claude.

The tools themselves live in the ``tools`` package, grouped by data area.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from tools import register_all

_BEARER_TOKEN = os.environ.get("MCP_BEARER_TOKEN")
if not _BEARER_TOKEN:
    raise SystemExit(
        "MCP_BEARER_TOKEN is not set. Provide a secret bearer token "
        "(e.g. `openssl rand -hex 32`) via the environment / .env file."
    )

auth = StaticTokenVerifier(tokens={_BEARER_TOKEN: {"client_id": "claude"}})
mcp = FastMCP("garmin", auth=auth)
register_all(mcp)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
