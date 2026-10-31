"""Garmin Connect Personal API client.

Authenticates with a Personal API key (created in Garmin Connect Web under
Settings -> Personal API Key) given in the ``GARMIN_API_KEY`` environment
variable. The key is exchanged for an access token that is valid for 24 hours;
there are no refresh tokens, so a new token is simply requested from the key
before the old one expires (or when Garmin rejects it).

API reference: https://developer.garmin.com/gc-developer-program/personal/swagger-docs/
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any

import httpx

_BASE_URL = "https://personal.connectapi.garmin.com"
_TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
# Tokens live 24h; renew an hour early so a request never races the expiry.
_TOKEN_MAX_AGE = 23 * 3600

_http = httpx.Client(base_url=_BASE_URL, timeout=30)
_lock = threading.Lock()
_token: str | None = None
_token_issued = 0.0


class GarminAuthError(RuntimeError):
    """Raised when the Personal API key is missing, invalid or expired."""


def _fetch_token() -> str:
    key = os.environ.get("GARMIN_API_KEY")
    if not key:
        raise GarminAuthError(
            "GARMIN_API_KEY is not set. Create a Personal API key in Garmin Connect "
            "Web (Settings -> Personal API Key) and add it to .env (see README)."
        )
    resp = _http.post(_TOKEN_PATH, headers={"Authorization": f"ApiKey {key}"})
    if resp.status_code in (401, 403):
        raise GarminAuthError(
            f"Garmin rejected the Personal API key (HTTP {resp.status_code}). It may "
            "have expired or been deleted; create a new one in Garmin Connect Web."
        )
    resp.raise_for_status()
    # shortcut: the token response schema is undocumented, so accept the usual
    # field names or a plain-text body; pin it once verified against a real key.
    try:
        body = resp.json()
    except ValueError:
        token = resp.text.strip()
    else:
        token = (
            (body.get("access_token") or body.get("accessToken"))
            if isinstance(body, dict)
            else body if isinstance(body, str) else None
        )
        if not token:
            fields = sorted(body) if isinstance(body, dict) else type(body).__name__
            raise GarminAuthError(f"Unexpected token response from Garmin: {fields}")
    return token


def _get_token(renew: bool = False) -> str:
    global _token, _token_issued
    with _lock:
        if renew or _token is None or time.monotonic() - _token_issued > _TOKEN_MAX_AGE:
            _token = _fetch_token()
            _token_issued = time.monotonic()
        return _token


def api_get(path: str, params: dict[str, Any] | None = None, *, raw: bool = False) -> Any:
    """GET a Personal API endpoint and return the decoded JSON (or bytes if ``raw``).

    ``None`` values in ``params`` are dropped so tools can pass optional filters
    straight through. Returns ``None`` for an empty response (e.g. HTTP 204).
    """
    params = {k: v for k, v in (params or {}).items() if v is not None}
    resp = _http.get(path, params=params, headers={"Authorization": f"Bearer {_get_token()}"})
    if resp.status_code == 401:  # token revoked or expired early: renew once and retry
        resp = _http.get(
            path, params=params, headers={"Authorization": f"Bearer {_get_token(renew=True)}"}
        )
    resp.raise_for_status()
    if raw:
        return resp.content
    return resp.json() if resp.content else None
