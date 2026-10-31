"""Tests for download_activity_file (run: python -m unittest)."""

from __future__ import annotations

import asyncio
import base64
import io
import unittest
import zipfile
from unittest import mock

from fastmcp import Client, FastMCP

from tools import activities


def _zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buf.getvalue()


def _download(zip_bytes: bytes):
    mcp = FastMCP("test")
    activities.register(mcp)

    async def call():
        async with Client(mcp) as client:
            result = await client.call_tool("download_activity_file", {"activity_id": 1})
            return result.content[0].resource

    with mock.patch.object(activities, "api_get", return_value=zip_bytes):
        return asyncio.run(call())


class DownloadActivityFileTest(unittest.TestCase):
    def test_single_file_is_unpacked(self):
        resource = _download(_zip({"1_ACTIVITY.fit": b"FITDATA"}))
        self.assertEqual(base64.b64decode(resource.blob), b"FITDATA")
        self.assertTrue(str(resource.uri).endswith("1_ACTIVITY.fit"))

    def test_multiple_files_stay_zipped(self):
        data = _zip({"a.fit": b"A", "b.fit": b"B"})
        resource = _download(data)
        self.assertEqual(base64.b64decode(resource.blob), data)


if __name__ == "__main__":
    unittest.main()
