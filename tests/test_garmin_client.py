"""Tests for the Personal API client (run: python -m unittest)."""

from __future__ import annotations

import os
import unittest
from unittest import mock

import httpx

import garmin_client
from tools._common import day


class ApiGetTest(unittest.TestCase):
    def setUp(self):
        self.requests: list[httpx.Request] = []
        self.tokens = iter(["t1", "t2"])
        self.reject_first_get = False
        transport = httpx.MockTransport(self._handle)
        patches = [
            mock.patch.object(
                garmin_client, "_http", httpx.Client(base_url="https://x", transport=transport)
            ),
            mock.patch.object(garmin_client, "_token", None),
            mock.patch.dict(os.environ, {"GARMIN_API_KEY": "k"}),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"access_token": next(self.tokens)})
        if self.reject_first_get:
            self.reject_first_get = False
            return httpx.Response(401)
        return httpx.Response(200, json={"ok": True})

    def test_drops_none_params_and_sends_bearer(self):
        self.assertEqual(garmin_client.api_get("/p", {"a": 1, "b": None}), {"ok": True})
        token_req, get_req = self.requests
        self.assertEqual(token_req.headers["Authorization"], "ApiKey k")
        self.assertEqual(get_req.url.params, httpx.QueryParams({"a": "1"}))
        self.assertEqual(get_req.headers["Authorization"], "Bearer t1")

    def test_token_is_reused(self):
        garmin_client.api_get("/p")
        garmin_client.api_get("/p")
        self.assertEqual([r.method for r in self.requests], ["POST", "GET", "GET"])

    def test_renews_token_once_on_401(self):
        self.reject_first_get = True
        self.assertEqual(garmin_client.api_get("/p"), {"ok": True})
        self.assertEqual(self.requests[-1].headers["Authorization"], "Bearer t2")

    def test_missing_key(self):
        with mock.patch.dict(os.environ, {"GARMIN_API_KEY": ""}):
            with self.assertRaises(garmin_client.GarminAuthError):
                garmin_client.api_get("/p")


class DayTest(unittest.TestCase):
    def test_rejects_non_dates(self):
        self.assertEqual(day("2026-10-01"), "2026-10-01")
        with self.assertRaises(ValueError):
            day("../../userprofile-service")


if __name__ == "__main__":
    unittest.main()
