"""Training tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import get_client

from ._common import today


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_training_status(date: str | None = None) -> Any:
        """Get training status (productive, maintaining, detraining, etc.) for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_training_status(date or today())

    @mcp.tool
    def get_training_readiness(date: str | None = None) -> Any:
        """Get training readiness score and its contributing factors for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_training_readiness(date or today())

    @mcp.tool
    def get_training_load(date: str | None = None) -> Any:
        """Get training load metrics (acute/chronic load, load balance) for a day.

        Garmin returns load metrics as part of the training-status payload.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_training_status(date or today())

    @mcp.tool
    def get_vo2max(date: str | None = None) -> Any:
        """Get VO2max / fitness metrics (max metrics) for a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return get_client().get_max_metrics(date or today())
