"""Shared helpers for the Garmin tool modules."""

from __future__ import annotations

from datetime import date as _date


def today() -> str:
    """Return today's date as an ISO `YYYY-MM-DD` string."""
    return _date.today().isoformat()


def day(value: str | None) -> str:
    """Validate a `YYYY-MM-DD` date argument, defaulting to today.

    Dates end up in URL paths, so anything that is not a plain date is rejected.
    """
    return _date.fromisoformat(value).isoformat() if value else today()
