"""Authorization middleware: restrict access to a single GitHub user.

GitHub OAuth (via FastMCP's ``GitHubProvider``) authenticates *anyone* with a
GitHub account. This middleware narrows that to the single owner by comparing
the authenticated user's GitHub login against an allowlist of one. It fails
closed: if no identity can be determined, access is denied.
"""

from __future__ import annotations

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import Middleware


class GitHubUserAllowlist(Middleware):
    """Allow only a specific GitHub login to list or call tools."""

    def __init__(self, allowed_login: str) -> None:
        self._allowed = allowed_login.strip().lower()
        if not self._allowed:
            raise ValueError("ALLOWED_GITHUB_USER must not be empty.")

    def _assert_owner(self) -> None:
        # KNOWN DEBT (security): we match on the GitHub *login*, which is
        # mutable. If the owner renames their GitHub account, the freed
        # username could be claimed by someone else who would then pass this
        # check. Hardening: match on the immutable numeric id (claims["sub"]).
        # Accepted for now; see README "Security notes".
        token = get_access_token()
        claims = getattr(token, "claims", None) or {}
        login = (claims.get("login") or "").strip().lower()
        if not login or login != self._allowed:
            raise ToolError(
                "Access denied: this connector is restricted to its owner."
            )

    async def on_call_tool(self, context, call_next):
        self._assert_owner()
        return await call_next(context)

    async def on_list_tools(self, context, call_next):
        self._assert_owner()
        return await call_next(context)
