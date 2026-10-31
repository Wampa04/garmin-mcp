"""Body composition, fitness age, nutrition and profile tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from garmin_client import api_get

from ._common import day


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def get_fitness_age(date: str | None = None) -> Any:
        """Get the latest Fitness Age (and its components) as of a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/fitnessage-service/fitnessage/v2/{day(date)}")

    @mcp.tool
    def get_weight(
        start_date: str | None = None,
        end_date: str | None = None,
        include_all: bool = False,
    ) -> Any:
        """Get weight summaries for a date range (latest weight per day and range average).

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
            include_all: Include every weigh-in per day instead of only the latest.
        """
        return api_get(
            f"/weight-service/weight/range/{day(start_date)}/{day(end_date)}",
            {"includeAll": include_all},
        )

    @mcp.tool
    def get_weight_entries(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get all individual weight entries for a date range.

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/weight-service/weight/all/{day(start_date)}/{day(end_date)}")

    @mcp.tool
    def get_weight_goals(start_date: str | None = None, end_date: str | None = None) -> Any:
        """Get the effective weight goals for a date range.

        Args:
            start_date: Range start (defaults to today), format YYYY-MM-DD.
            end_date: Range end (defaults to today), format YYYY-MM-DD.
        """
        return api_get(
            f"/goal-service/goal/user/effective/weightgoal/{day(start_date)}/{day(end_date)}"
        )

    @mcp.tool
    def get_nutrition_log(date: str | None = None, meal_id: int | None = None) -> Any:
        """Get the nutrition log for a day: goals, nutrients consumed and meals.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
            meal_id: Optional meal id to restrict the breakdown to one meal.
        """
        # Food photos are of no use to Claude and only bloat the response.
        return api_get(
            f"/nutrition-service/food/logs/{day(date)}",
            {"includeMedia": False, "mealId": meal_id},
        )

    @mcp.tool
    def get_menstrual_cycle_summary(date: str | None = None) -> Any:
        """Get the menstrual cycle summary as of a day.

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
        """
        return api_get(f"/periodichealth-service/menstrualcycle/summary/{day(date)}")

    @mcp.tool
    def get_menstrual_cycle_day(date: str | None = None, include_analysis: bool = False) -> Any:
        """Get detailed menstrual cycle data for one day (logged symptoms, flow, mood, phase).

        Args:
            date: Day to query (defaults to today), format YYYY-MM-DD.
            include_analysis: Also include the cycle analysis.
        """
        return api_get(
            f"/periodichealth-service/menstrualcycle/dayview/{day(date)}",
            {"todayDate": day(None), "includeAnalysis": include_analysis},
        )

    @mcp.tool
    def get_user_settings() -> Any:
        """Get the user's profile settings (units, formats, time zone, training days)."""
        return api_get("/userprofile-service/userprofile/settings")
