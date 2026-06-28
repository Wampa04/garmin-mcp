"""Garmin Connect MCP server.

Exposes 17 read-only tools over Garmin Connect data via the MCP HTTP
transport, protected by a static bearer token. Designed to run as a Docker
container behind Traefik and be added as a Custom Connector in Claude.
"""

from __future__ import annotations

import os
from datetime import date as _date
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from garmin_client import get_client

_BEARER_TOKEN = os.environ.get("MCP_BEARER_TOKEN")
if not _BEARER_TOKEN:
    raise SystemExit(
        "MCP_BEARER_TOKEN is not set. Provide a secret bearer token "
        "(e.g. `openssl rand -hex 32`) via the environment / .env file."
    )

auth = StaticTokenVerifier(tokens={_BEARER_TOKEN: {"client_id": "claude"}})
mcp = FastMCP("garmin", auth=auth)


def _today() -> str:
    return _date.today().isoformat()


# --------------------------------------------------------------------------- #
# Activities
# --------------------------------------------------------------------------- #
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
        start_date, end_date or _today(), activity_type
    )


# --------------------------------------------------------------------------- #
# Sleep / recovery
# --------------------------------------------------------------------------- #
@mcp.tool
def get_sleep(date: str | None = None) -> Any:
    """Get sleep data (stages, duration, scores) for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_sleep_data(date or _today())


@mcp.tool
def get_body_battery(start_date: str, end_date: str | None = None) -> Any:
    """Get Body Battery energy levels over a date range (YYYY-MM-DD).

    Args:
        start_date: Range start, format YYYY-MM-DD.
        end_date: Range end (defaults to today if omitted), format YYYY-MM-DD.
    """
    return get_client().get_body_battery(start_date, end_date or _today())


@mcp.tool
def get_hrv(date: str | None = None) -> Any:
    """Get heart rate variability (HRV) data for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_hrv_data(date or _today())


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #
@mcp.tool
def get_training_status(date: str | None = None) -> Any:
    """Get training status (productive, maintaining, detraining, etc.) for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_training_status(date or _today())


@mcp.tool
def get_training_readiness(date: str | None = None) -> Any:
    """Get training readiness score and its contributing factors for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_training_readiness(date or _today())


@mcp.tool
def get_training_load(date: str | None = None) -> Any:
    """Get training load metrics (acute/chronic load, load balance) for a day.

    Garmin returns load metrics as part of the training-status payload.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_training_status(date or _today())


@mcp.tool
def get_vo2max(date: str | None = None) -> Any:
    """Get VO2max / fitness metrics (max metrics) for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_max_metrics(date or _today())


# --------------------------------------------------------------------------- #
# Heart rate / stress
# --------------------------------------------------------------------------- #
@mcp.tool
def get_heart_rate(date: str | None = None) -> Any:
    """Get heart rate readings throughout a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_heart_rates(date or _today())


@mcp.tool
def get_resting_heart_rate(date: str | None = None) -> Any:
    """Get the resting heart rate for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_rhr_day(date or _today())


@mcp.tool
def get_stress(date: str | None = None) -> Any:
    """Get all-day stress level data for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_stress_data(date or _today())


# --------------------------------------------------------------------------- #
# Daily activity / records
# --------------------------------------------------------------------------- #
@mcp.tool
def get_daily_summary(date: str | None = None) -> Any:
    """Get the daily wellness summary (steps, calories, intensity minutes, etc.).

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_user_summary(date or _today())


@mcp.tool
def get_steps(date: str | None = None) -> Any:
    """Get intraday step counts for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_steps_data(date or _today())


@mcp.tool
def get_floors(date: str | None = None) -> Any:
    """Get floors climbed/descended for a day.

    Args:
        date: Day to query (defaults to today), format YYYY-MM-DD.
    """
    return get_client().get_floors(date or _today())


@mcp.tool
def get_personal_records() -> Any:
    """Get the user's personal records across activity types."""
    return get_client().get_personal_record()


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
