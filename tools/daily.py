"""Daily activity and personal records tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import get_client

from ._common import today


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_daily_summary(date: str | None = None) -> Any:
        """Get the daily wellness summary (steps, calories, intensity minutes, etc.).

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_user_summary(date or today())

    @mcp.tool
    def get_steps(date: str | None = None) -> Any:
        """Get intraday step counts for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_steps_data(date or today())

    @mcp.tool
    def get_floors(date: str | None = None) -> Any:
        """Get floors climbed/descended for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_floors(date or today())

    @mcp.tool
    def get_personal_records() -> Any:
        """Get the user's personal records across activity types."""
        return get_client().get_personal_record()
