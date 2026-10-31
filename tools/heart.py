"""Heart rate and stress tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import api_get

from ._common import day


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_heart_rate(date: str | None = None) -> Any:
        """Get heart rate readings throughout a day (incl. min/max/resting).

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get("/wellness-service/wellness/dailyHeartRate", {"date": day(date)})

    @mcp.tool
    def get_resting_heart_rate(date: str | None = None) -> Any:
        """Get the resting heart rate for a day and its 7-day average.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        hr = api_get("/wellness-service/wellness/dailyHeartRate", {"date": day(date)}) or {}
        return {
            k: hr.get(k)
            for k in ("calendarDate", "restingHeartRate", "lastSevenDaysAvgRestingHeartRate")
        }

    @mcp.tool
    def get_heart_rate_zones() -> Any:
        """Get the user's configured heart rate zones."""
        return api_get("/biometric-service/heartRateZones/v2")

    @mcp.tool
    def get_stress(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily stress levels for a date range (max. 28 days).

        Detailed stress durations for a single day are in `get_daily_summary`.

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            f"/usersummary-service/stats/stress/daily/{day(start_date)}/{day(end_date)}"
        )
