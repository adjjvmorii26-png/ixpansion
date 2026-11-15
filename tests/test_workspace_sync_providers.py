from __future__ import annotations

import json
import unittest
from urllib.parse import parse_qs, urlparse

from integrations.workspace_sync.providers import (
    GoogleDriveMetadataAdapter,
    NotionDatabaseAdapter,
    ProviderConfigurationError,
    ProviderProtocolError,
)
from integrations.workspace_sync.outbox import PermanentAdapterError, TransientAdapterError


def event(target="notion"):
    return {
        "idempotency_key": "github:commit:abc123:" + target + ":upsert",
        "payload_hash": "unused",
        "payload": {
            "artifact_id": "artifact-9",
            "title": "IXPANSION validation report",
            "source_revision": "abc123",
            "url": "https://example.invalid/report",
        },
    }


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.pages = {}
        self.files = {}
        self.next_id = 0

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append((method, url, headers, body, timeout))
        payload = json.loads(body) if body else {}
        parsed = urlparse(url)
        if parsed.netloc == "api.notion.com":
            if parsed.path.endswith("/query"):
                key = payload["filter"]["rich_text"]["equals"]
                rows = [p for p in self.pages.values() if p["properties"]["IXPANSION Key"]["rich_text"][0]["plain_text"] == key]
                return 200, {"results": rows}
            if parsed.path == "/v1/pages" and method == "POST":
                self.next_id += 1
                page_id = f"page-{self.next_id}"
                props = payload["properties"]
                self.pages[page_id] = {"id": page_id, "properties": self._notion_props(props)}
                return 200, {"id": page_id}
            if parsed.path.startswith("/v1/pages/") and method == "PATCH":
                page_id = parsed.path.rsplit("/", 1)[-1]
                self.pages[page_id]["properties"] = self._notion_props(payload["properties"])
                return 200, {"id": page_id}
            if parsed.path.startswith("/v1/pages/") and method == "GET":
                return 200, self.pages[parsed.path.rsplit("/", 1)[-1]]
        if parsed.netloc == "www.googleapis.com":
            if parsed.path.endswith("/files") and method == "GET":
                key = parse_qs(parsed.query)["q"][0].split("value='", 1)[1].split("'", 1)[0]
                return 200, {"files": [f for f in self.files.values() if f["appProperties"]["ixpansion_key"] == key]}
            if parsed.path.endswith("/files") and method == "POST":
                self.next_id += 1
                file_id = f"file-{self.next_id}"
                self.files[file_id] = {"id": file_id, **payload, "webViewLink": f"https://drive.invalid/{file_id}"}
                return 200, {"id": file_id}
            if "/files/" in parsed.path and method == "PATCH":
                file_id = parsed.path.rsplit("/", 1)[-1]
                self.files[file_id].update(payload)
                return 200, {"id": file_id}
            if "/files/" in parsed.path and method == "GET":
                return 200, self.files[parsed.path.rsplit("/", 1)[-1]]
        raise AssertionError(f"unexpected request: {method} {url}")

    @staticmethod
    def _notion_props(props):
        result = {}
        for name, value in props.items():
            kind = "title" if "title" in value else "rich_text"
            text = value[kind][0]["text"]["content"]
            result[name] = {kind: [{"plain_text": text}]}
        return result


class ProviderAdapterTests(unittest.TestCase):
    def test_missing_credentials_fail_closed(self):
        with self.assertRaises(ProviderConfigurationError):
            NotionDatabaseAdapter(database_id="db", token="")
        with self.assertRaises(ProviderConfigurationError):
            GoogleDriveMetadataAdapter(token="")

    def test_notion_upsert_is_replay_safe_and_readback_verified(self):
        fake = FakeTransport()
        adapter = NotionDatabaseAdapter(database_id="db", token="test-token", transport=fake)
        item = event()
        receipt = adapter.deliver(item)
        self.assertTrue(adapter.verify(item, receipt))
        replay = adapter.deliver(item)
        self.assertEqual(receipt["page_id"], replay["page_id"])
        self.assertEqual(len(fake.pages), 1)
        self.assertEqual([call[0] for call in fake.calls].count("POST"), 2)  # query + create

    def test_notion_revision_update_targets_existing_page(self):
        fake = FakeTransport()
        adapter = NotionDatabaseAdapter(database_id="db", token="test-token", transport=fake)
        first = event()
        receipt = adapter.deliver(first)
        updated = {**first, "payload": {**first["payload"], "source_revision": "def456"}}
        receipt2 = adapter.deliver(updated)
        self.assertEqual(receipt["page_id"], receipt2["page_id"])
        self.assertEqual(len(fake.pages), 1)
        self.assertTrue(adapter.verify(updated, receipt2))

    def test_drive_upsert_is_replay_safe_and_readback_verified(self):
        fake = FakeTransport()
        adapter = GoogleDriveMetadataAdapter(token="test-token", transport=fake)
        item = event("drive")
        receipt = adapter.deliver(item)
        self.assertTrue(adapter.verify(item, receipt))
        replay = adapter.deliver(item)
        self.assertEqual(receipt["file_id"], replay["file_id"])
        self.assertEqual(len(fake.files), 1)

    def test_drive_revision_update_targets_existing_file(self):
        fake = FakeTransport()
        adapter = GoogleDriveMetadataAdapter(token="test-token", transport=fake)
        first = event("drive")
        receipt = adapter.deliver(first)
        updated = {**first, "payload": {**first["payload"], "source_revision": "def456"}}
        receipt2 = adapter.deliver(updated)
        self.assertEqual(receipt["file_id"], receipt2["file_id"])
        self.assertEqual(len(fake.files), 1)
        self.assertTrue(adapter.verify(updated, receipt2))

    def test_duplicate_remote_artifacts_are_quarantined(self):
        fake = FakeTransport()
        adapter = GoogleDriveMetadataAdapter(token="test-token", transport=fake)
        item = event("drive")
        fake.files["f1"] = {"id": "f1", **adapter._metadata(item)}
        fake.files["f2"] = {"id": "f2", **adapter._metadata(item)}
        with self.assertRaises(ProviderProtocolError):
            adapter.deliver(item)

    def test_http_failure_classes_are_not_swallowed(self):
        def forbidden(*args):
            return 403, {"error": "forbidden"}
        def unavailable(*args):
            return 503, {"error": "busy"}
        notion = NotionDatabaseAdapter(database_id="db", token="test-token", transport=forbidden)
        with self.assertRaises(PermanentAdapterError):
            notion.deliver(event())
        notion = NotionDatabaseAdapter(database_id="db", token="test-token", transport=unavailable)
        with self.assertRaises(TransientAdapterError):
            notion.deliver(event())

    def test_invalid_urls_are_rejected_before_write(self):
        fake = FakeTransport()
        adapter = GoogleDriveMetadataAdapter(token="test-token", transport=fake)
        item = event("drive")
        item["payload"]["url"] = "file:///etc/passwd"
        with self.assertRaises(ProviderProtocolError):
            adapter.deliver(item)
        self.assertEqual(fake.calls, [])


if __name__ == "__main__":
    unittest.main()
