"""Heart rate and stress tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import get_client

from ._common import today


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_heart_rate(date: str | None = None) -> Any:
        """Get heart rate readings throughout a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_heart_rates(date or today())

    @mcp.tool
    def get_resting_heart_rate(date: str | None = None) -> Any:
        """Get the resting heart rate for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_rhr_day(date or today())

    @mcp.tool
    def get_stress(date: str | None = None) -> Any:
        """Get all-day stress level data for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_stress_data(date or today())
