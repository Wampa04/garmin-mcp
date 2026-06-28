"""Shared helpers for the Garmin tool modules."""

from __future__ import annotations

from datetime import date as _date


def today() -> str:
    """Return today's date as an ISO `YYYY-MM-DD` string."""
    return _date.today().isoformat()
