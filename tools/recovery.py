"""Sleep and recovery tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import get_client

from ._common import today


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_sleep(date: str | None = None) -> Any:
        """Get sleep data (stages, duration, scores) for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_sleep_data(date or today())

    @mcp.tool
    def get_body_battery(start_date: str, end_date: str | None = None) -> Any:
        """Get Body Battery energy levels over a date range (YYYY-MM-DD).

        Args:
            start_date: Range start, format YYYY-MM-DD.
            end_date: Range end (defaults to today if omitted), format YYYY-MM-DD.
        """
        return get_client().get_body_battery(start_date, end_date or today())

    @mcp.tool
    def get_hrv(date: str | None = None) -> Any:
        """Get heart rate variability (HRV) data for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_hrv_data(date or today())
