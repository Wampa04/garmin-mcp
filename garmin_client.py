"""Garmin Connect client wrapper.

Uses token-resume authentication only: the garth session tokens must be
generated once locally (interactive, handles MFA) via
``scripts/generate_tokens.py`` and mounted into the container at the path
given by the ``GARMINTOKENS`` environment variable.

The container never logs in with email/password, which avoids the
captcha/MFA blocks Garmin applies to logins from datacenter IPs.
"""

from __future__ import annotations

import os
import threading

from garminconnect import Garmin

# Default matches the read-only volume mount in docker-compose.yml.
_TOKENSTORE = os.environ.get("GARMINTOKENS", "/tokens")

_client: Garmin | None = None
_lock = threading.Lock()


class GarminAuthError(RuntimeError):
    """Raised when the stored garth tokens are missing or invalid."""


def get_client() -> Garmin:
    """Return a logged-in Garmin client, creating it on first use.

    The client is a process-wide singleton; garth refreshes the session
    tokens automatically before each request, so a single login is enough
    for the lifetime of the process. Guarded by a lock so concurrent MCP
    requests do not trigger a duplicate login.
    """
    global _client
    if _client is not None:
        return _client

    with _lock:
        if _client is not None:  # another thread won the race
            return _client

        if not os.path.isdir(_TOKENSTORE) or not os.listdir(_TOKENSTORE):
            raise GarminAuthError(
                f"No Garmin tokens found in '{_TOKENSTORE}'. Generate them locally "
                "with `python scripts/generate_tokens.py` and mount the resulting "
                "directory into the container (see README)."
            )

        client = Garmin()
        try:
            client.login(_TOKENSTORE)
        except Exception as exc:  # noqa: BLE001 - surface a clear, actionable message
            raise GarminAuthError(
                f"Could not log in to Garmin using tokens in '{_TOKENSTORE}': {exc}. "
                "The tokens may have expired; regenerate them with "
                "`python scripts/generate_tokens.py`."
            ) from exc

        _client = client
        return _client
