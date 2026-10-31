"""Activity tools."""

from __future__ import annotations

import io
import zipfile
from pathlib import PurePath
from typing import Any

from fastmcp import FastMCP
from fastmcp.utilities.types import File

from garmin_client import api_get

from ._common import day

_SEARCH = "/activitylist-service/activities/search/activities"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def list_activities(limit: int = 10, start: int = 0) -> Any:
        """List the most recent Garmin activities (newest first).

        Each activity includes VO2max, training effect and training load.

        Args:
            limit: Maximum number of activities to return.
            start: Zero-based offset, for paging through older activities.
        """
        return api_get(_SEARCH, {"start": start, "limit": limit})

    @mcp.tool
    def search_activities(
        search: str | None = None,
        activity_type: str | None = None,
        activity_sub_type: str | None = None,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        min_distance_m: int | None = None,
        max_distance_m: int | None = None,
        min_duration_s: int | None = None,
        max_duration_s: int | None = None,
        min_elevation_gain_m: int | None = None,
        max_elevation_gain_m: int | None = None,
        min_avg_power_w: int | None = None,
        favorites_only: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 20,
        start: int = 0,
    ) -> Any:
        """Search activities by text and filters. All filters are optional and combined.

        Each activity includes VO2max, training effect and training load.

        Args:
            search: Text to find in activity names and descriptions.
            activity_type: Parent type key, e.g. "running", "cycling".
            activity_sub_type: Subtype key, e.g. "trail_running" (with activity_type "running").
            event_type: e.g. "race", "training", "recreation", "fitness", "uncategorized".
            start_date: Earliest start date, format YYYY-MM-DD.
            end_date: Latest start date, format YYYY-MM-DD.
            min_distance_m: Minimum distance in meters.
            max_distance_m: Maximum distance in meters.
            min_duration_s: Minimum timer duration in seconds.
            max_duration_s: Maximum timer duration in seconds.
            min_elevation_gain_m: Minimum total elevation gain in meters.
            max_elevation_gain_m: Maximum total elevation gain in meters.
            min_avg_power_w: Minimum average power in watts.
            favorites_only: Only return activities marked as favorite.
            sort_by: Field to sort by, e.g. "name", "distance", "duration" (default: start time).
            sort_order: "asc" or "desc".
            limit: Maximum number of activities to return.
            start: Zero-based offset for paging.
        """
        return api_get(
            _SEARCH,
            {
                "search": search,
                "activityType": activity_type,
                "activitySubType": activity_sub_type,
                "eventType": event_type,
                "startDate": day(start_date) if start_date else None,
                "endDate": day(end_date) if end_date else None,
                "minDistance": min_distance_m,
                "maxDistance": max_distance_m,
                "minDuration": min_duration_s,
                "maxDuration": max_duration_s,
                "minElevation": min_elevation_gain_m,
                "maxElevation": max_elevation_gain_m,
                "minAvgPower": min_avg_power_w,
                "favorite": 1 if favorites_only else None,
                "sortBy": sort_by,
                "sortOrder": sort_order,
                "limit": limit,
                "start": start,
            },
        )

    @mcp.tool
    def get_activity_details(activity_id: int) -> Any:
        """Get the summary, metrics and splits of one activity.

        Includes training effect and training load (VO2max is in
        `list_activities` / `search_activities`). Second-by-second data (GPS
        track, HR curve) is only in the original file, see `download_activity_file`.

        Args:
            activity_id: The Garmin activity id, as returned by `list_activities`.
        """
        return api_get(f"/activity-service/activity/{activity_id}")

    @mcp.tool
    def get_activity_workouts(activity_id: int) -> Any:
        """Get the structured workouts performed during an activity.

        Args:
            activity_id: The Garmin activity id, as returned by `list_activities`.
        """
        return api_get(f"/activity-service/activity/{activity_id}/workouts")

    @mcp.tool
    def download_activity_file(activity_id: int) -> File:
        """Download the original activity file (usually .FIT; GPX/TCX for uploaded activities).

        Args:
            activity_id: The Garmin activity id, as returned by `list_activities`.
        """
        data = api_get(f"/download-service/files/activity/{activity_id}", raw=True)
        # Garmin wraps the original file in a ZIP; unwrap it when it holds just one.
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = [e for e in archive.infolist() if not e.is_dir()]
            if len(entries) == 1:
                name = PurePath(entries[0].filename)
                return File(
                    data=archive.read(entries[0]),
                    format=name.suffix.lstrip(".").lower() or None,
                    name=name.stem,
                )
        return File(data=data, format="zip", name=f"activity_{activity_id}")

    @mcp.tool
    def get_wellness_activity_summaries(
        start_date: str | None = None, end_date: str | None = None
    ) -> Any:
        """Get wellness activity summaries for a date range (YYYY-MM-DD).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            f"/wellnessactivity-service/activity/summary/range/{day(start_date)}/{day(end_date)}"
        )
