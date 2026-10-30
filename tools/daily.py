"""Daily wellness summary tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import api_get

from ._common import day

_DAILY = "/usersummary-service/usersummary/daily"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_daily_summary(date: str | None = None) -> Any:
        """Get the daily wellness summary for a day.

        Covers steps, calories, intensity minutes, floors, heart rate, stress,
        Body Battery, SpO2 and respiration.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get(_DAILY, {"calendarDate": day(date)})

    @mcp.tool
    def get_daily_summaries(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily wellness summaries for a date range (max. 1 year).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            "/usersummary-service/v2/dailysummaries",
            {"startDate": day(start_date), "endDate": day(end_date)},
        )

    @mcp.tool
    def get_steps(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily step totals for a date range (max. 28 days).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            f"/usersummary-service/stats/steps/daily/{day(start_date)}/{day(end_date)}"
        )

    @mcp.tool
    def get_floors(date: str | None = None) -> Any:
        """Get floors climbed/descended for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        summary = api_get(_DAILY, {"calendarDate": day(date)}) or {}
        return {
            k: summary.get(k)
            for k in (
                "calendarDate",
                "floorsAscended",
                "floorsDescended",
                "floorsAscendedInMeters",
                "floorsDescendedInMeters",
                "userFloorsAscendedGoal",
            )
        }

    @mcp.tool
    def get_hydration(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily hydration (fluid intake) for a date range (max. 31 days).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            f"/usersummary-service/stats/hydration/daily/{day(start_date)}/{day(end_date)}"
        )
