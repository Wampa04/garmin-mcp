"""Garmin Connect MCP server.

Exposes 29 read-only tools over the Garmin Connect Personal API via the MCP
HTTP transport. Designed to run as a Docker container behind Traefik and be added
as a Custom Connector in Claude.

Access is protected by **GitHub OAuth**: Claude runs the OAuth 2.1 flow
(dynamic client registration + PKCE) against this server, which proxies to
GitHub. A middleware then restricts access to a single GitHub user, so only
the owner can reach the data. You paste only the URL into Claude and log in
with GitHub — no client id/secret to enter, no token to copy.

The tools themselves live in the ``tools`` package, grouped by data area.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

from auth import GitHubUserAllowlist
from tools import register_all


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set. See .env.example.")
    return value


_CLIENT_ID = _require("GITHUB_CLIENT_ID")
_CLIENT_SECRET = _require("GITHUB_CLIENT_SECRET")
_ALLOWED_USER = _require("ALLOWED_GITHUB_USER")
_require("GARMIN_API_KEY")  # read by garmin_client; checked here so a missing key fails at startup
# Public base URL where OAuth endpoints live (e.g. https://garmin-mcp.example.de).
# Defaults to https://<GARMIN_MCP_DOMAIN>; override with MCP_BASE_URL if needed.
_BASE_URL = os.environ.get("MCP_BASE_URL") or f"https://{_require('GARMIN_MCP_DOMAIN')}"

# Restrict which client redirect URIs may be registered via dynamic client
# registration. Without this, ANY client could register an arbitrary redirect
# URI; if the owner then click-throughs the consent screen, an attacker-
# registered client could capture an auth code minted for the owner's identity
# and bypass the allowlist. Default to Claude's callback hosts; override with
# ALLOWED_CLIENT_REDIRECT_URIS (comma-separated fnmatch patterns) for other
# clients. Host is matched exactly (or via *.domain), path via fnmatch.
_DEFAULT_REDIRECT_URIS = "https://claude.ai/*,https://claude.com/*"
_redirect_uris = [
    u.strip()
    for u in os.environ.get(
        "ALLOWED_CLIENT_REDIRECT_URIS", _DEFAULT_REDIRECT_URIS
    ).split(",")
    if u.strip()
]

# Optional: a stable signing key so tokens issued to Claude survive container
# restarts (otherwise a new key is generated each start, forcing re-login).
_provider_kwargs: dict[str, object] = {
    "client_id": _CLIENT_ID,
    "client_secret": _CLIENT_SECRET,
    "base_url": _BASE_URL,
    "allowed_client_redirect_uris": _redirect_uris,
}
if os.environ.get("MCP_JWT_SECRET"):
    _provider_kwargs["jwt_signing_key"] = os.environ["MCP_JWT_SECRET"]

auth = GitHubProvider(**_provider_kwargs)

mcp = FastMCP("garmin", auth=auth)
mcp.add_middleware(GitHubUserAllowlist(_ALLOWED_USER))
register_all(mcp)


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health(_request):
    """Unauthenticated liveness probe for the container healthcheck."""
    from starlette.responses import JSONResponse

    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
