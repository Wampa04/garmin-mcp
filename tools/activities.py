"""Activity tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import get_client

from ._common import today


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def list_activities(limit: int = 10) -> Any:
        """List the most recent Garmin activities (newest first).

        Args:
            limit: Maximum number of activities to return.
        """
        return get_client().get_activities(0, limit)

    @mcp.tool
    def get_activity_details(activity_id: str) -> Any:
        """Get full details (splits, metrics, GPS summary) for one activity.

        Args:
            activity_id: The Garmin activity id, as returned by `list_activities`.
        """
        return get_client().get_activity_details(activity_id)

    @mcp.tool
    def list_activities_by_date(
        start_date: str,
        end_date: str | None = None,
        activity_type: str | None = None,
    ) -> Any:
        """List activities within a date range (YYYY-MM-DD).

        Args:
            start_date: Range start, format YYYY-MM-DD.
            end_date: Range end (defaults to today if omitted), format YYYY-MM-DD.
            activity_type: Optional filter, e.g. "running", "cycling", "swimming".
        """
        return get_client().get_activities_by_date(
            start_date, end_date or today(), activity_type
        )
