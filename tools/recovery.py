"""Sleep and recovery tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import api_get

from ._common import day


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_sleep(date: str | None = None) -> Any:
        """Get sleep data (stages, duration, sleep score, SpO2, respiration) for a night.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get("/sleep-service/sleep/dailySleep", {"date": day(date)})

    @mcp.tool
    def get_sleep_summaries(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily sleep summaries for a date range (max. 31 days).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            "/sleep-service/sleep/dailySleepSummariesByDate",
            {"startDate": day(start_date), "endDate": day(end_date)},
        )

    @mcp.tool
    def get_body_battery(
        start_date: str | None = None,
        end_date: str | None = None,
        chunks: int | None = None,
    ) -> Any:
        """Get Body Battery energy levels over a date range (max. 31 days).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
            chunks: Optional number of intervals per day; each reports its lowest
                and highest Body Battery value.
        """
        return api_get(
            "/wellness-service/wellness/bodyBattery/reports/daily",
            {"startDate": day(start_date), "endDate": day(end_date), "chunks": chunks},
        )

    @mcp.tool
    def get_hrv(date: str | None = None) -> Any:
        """Get heart rate variability (HRV) data for a night.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/hrv-service/hrv/{day(date)}")

    @mcp.tool
    def get_hrv_summaries(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get daily HRV summaries for a date range.

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/hrv-service/hrv/daily/{day(start_date)}/{day(end_date)}")

    @mcp.tool
    def get_spo2(date: str | None = None) -> Any:
        """Get blood oxygen (SpO2) readings for a day, incl. altitude acclimation data.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/wellness-service/wellness/daily/spo2acclimation/{day(date)}")
