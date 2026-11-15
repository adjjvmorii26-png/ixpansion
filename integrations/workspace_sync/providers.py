"""Bounded, credential-from-environment metadata adapters for Notion and Drive.

These adapters intentionally synchronize artifact pointers/metadata only. They do
not upload arbitrary file bytes, change sharing permissions, or delete remote data.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from .outbox import PermanentAdapterError, TransientAdapterError

Transport = Callable[[str, str, dict[str, str], bytes | None, float], tuple[int, dict[str, Any]]]


class ProviderConfigurationError(PermanentAdapterError):
    """Required runtime configuration is absent or invalid."""


class ProviderProtocolError(PermanentAdapterError):
    """Provider response is malformed or violates the adapter contract."""


def _stdlib_transport(method: str, url: str, headers: dict[str, str],
                      body: bytes | None, timeout: float) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ProviderProtocolError("provider response exceeded 2 MB limit")
            parsed = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(parsed, dict):
                raise ProviderProtocolError("provider returned a non-object response")
            return response.status, parsed
    except urllib.error.HTTPError as exc:
        # Provider response bodies are intentionally not copied into logs or queue state.
        exc.close()
        if exc.code == 429 or exc.code >= 500:
            raise TransientAdapterError(f"provider HTTP {exc.code}") from None
        raise PermanentAdapterError(f"provider HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Do not include exception repr: URL errors can contain request details.
        raise TransientAdapterError(f"provider transport failure: {type(exc).__name__}") from None


class _JsonProvider:
    def __init__(self, token: str, *, transport: Transport | None = None,
                 timeout: float = 8.0) -> None:
        if not token or not token.strip():
            raise ProviderConfigurationError("provider access token is required")
        self._token = token.strip()
        self._transport = transport or _stdlib_transport
        self._timeout = max(1.0, min(float(timeout), 20.0))

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None,
                 extra_headers: dict[str, str] | None = None) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode() if payload is not None else None
        try:
            status, result = self._transport(method, url, headers, body, self._timeout)
        except (PermanentAdapterError, TransientAdapterError):
            raise
        except Exception as exc:
            raise TransientAdapterError(f"provider transport adapter failed: {type(exc).__name__}") from None
        if status == 429 or status >= 500:
            raise TransientAdapterError(f"provider HTTP {status}")
        if status < 200 or status >= 300:
            raise PermanentAdapterError(f"provider HTTP {status}")
        if not isinstance(result, dict):
            raise ProviderProtocolError("provider returned a non-object response")
        return result


class NotionDatabaseAdapter(_JsonProvider):
    """Idempotent Notion database-page upsert keyed by event idempotency key."""

    def __init__(self, *, database_id: str | None = None, token: str | None = None,
                 title_property: str | None = None, key_property: str = "IXPANSION Key",
                 revision_property: str = "Source Revision",
                 transport: Transport | None = None, timeout: float = 8.0) -> None:
        self.database_id = (database_id or os.getenv("IXPANSION_NOTION_DATABASE_ID", "")).strip()
        if not self.database_id:
            raise ProviderConfigurationError("IXPANSION_NOTION_DATABASE_ID is required")
        self.title_property = title_property or os.getenv("IXPANSION_NOTION_TITLE_PROPERTY", "Name")
        self.key_property = key_property
        self.revision_property = revision_property
        super().__init__(token or os.getenv("NOTION_API_TOKEN", ""), transport=transport, timeout=timeout)

    def _headers(self) -> dict[str, str]:
        return {"Notion-Version": "2022-06-28"}

    def _properties(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = event["payload"]
        title = str(payload.get("title") or payload.get("artifact_id") or "").strip()
        revision = str(payload.get("source_revision") or "").strip()
        if not title or not revision:
            raise ProviderProtocolError("Notion pointer requires title/artifact_id and source_revision")
        props: dict[str, Any] = {
            self.title_property: {"title": [{"text": {"content": title[:2000]}}]},
            self.key_property: {"rich_text": [{"text": {"content": event["idempotency_key"][:2000]}}]},
            self.revision_property: {"rich_text": [{"text": {"content": revision[:2000]}}]},
        }
        url = payload.get("url")
        if url:
            if not str(url).startswith(("https://", "http://")):
                raise ProviderProtocolError("artifact url must be HTTP(S)")
            props["Artifact URL"] = {"url": str(url)}
        return props

    def _find(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        result = self._request(
            "POST",
            f"https://api.notion.com/v1/databases/{urllib.parse.quote(self.database_id, safe='')}/query",
            {"filter": {"property": self.key_property, "rich_text": {"equals": event["idempotency_key"]}}},
            self._headers(),
        )
        rows = result.get("results", [])
        if not isinstance(rows, list):
            raise ProviderProtocolError("Notion query results were malformed")
        if result.get("has_more"):
            raise ProviderProtocolError("Notion query is paginated; refusing an incomplete uniqueness check")
        return rows

    def deliver(self, event: dict[str, Any]) -> dict[str, Any]:
        props = self._properties(event)
        matches = self._find(event)
        if len(matches) > 1:
            raise ProviderProtocolError("duplicate Notion pages found for one idempotency key")
        if matches:
            page_id = matches[0].get("id")
            if not page_id:
                raise ProviderProtocolError("Notion query result omitted page id")
            result = self._request(
                "PATCH", f"https://api.notion.com/v1/pages/{urllib.parse.quote(page_id, safe='')}",
                {"properties": props}, self._headers(),
            )
        else:
            result = self._request(
                "POST", "https://api.notion.com/v1/pages",
                {"parent": {"database_id": self.database_id}, "properties": props},
                self._headers(),
            )
        page_id = result.get("id")
        if not page_id:
            raise ProviderProtocolError("Notion write response omitted page id")
        return {"page_id": page_id, "idempotency_key": event["idempotency_key"],
                "source_revision": str(event["payload"]["source_revision"])}

    def verify(self, event: dict[str, Any], receipt: dict[str, Any]) -> bool:
        page_id = receipt.get("page_id")
        if not page_id:
            return False
        page = self._request(
            "GET", f"https://api.notion.com/v1/pages/{urllib.parse.quote(str(page_id), safe='')}",
            extra_headers=self._headers(),
        )
        props = page.get("properties", {})
        try:
            key = "".join(x.get("plain_text", "") for x in props[self.key_property]["rich_text"])
            revision = "".join(x.get("plain_text", "") for x in props[self.revision_property]["rich_text"])
            title = "".join(x.get("plain_text", "") for x in props[self.title_property]["title"])
        except (KeyError, TypeError, AttributeError):
            return False
        expected_title = str(event["payload"].get("title") or event["payload"].get("artifact_id") or "").strip()[:2000]
        return (
            key == event["idempotency_key"]
            and revision == str(event["payload"]["source_revision"])
            and title == expected_title
            and (
                not event["payload"].get("url")
                or props.get("Artifact URL", {}).get("url") == event["payload"]["url"]
            )
        )


class GoogleDriveMetadataAdapter(_JsonProvider):
    """Idempotent Drive metadata upsert keyed by a private appProperties marker."""

    def __init__(self, *, parent_id: str | None = None, token: str | None = None,
                 transport: Transport | None = None, timeout: float = 8.0) -> None:
        self.parent_id = (parent_id or os.getenv("IXPANSION_DRIVE_PARENT_ID", "")).strip()
        super().__init__(token or os.getenv("GOOGLE_DRIVE_ACCESS_TOKEN", ""), transport=transport, timeout=timeout)

    @staticmethod
    def _escape_query(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _find(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        key = hashlib.sha256(event["idempotency_key"].encode("utf-8")).hexdigest()
        query = f"appProperties has {{ key='ixpansion_key' and value='{key}' }} and trashed=false"
        url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode({
            "q": query, "spaces": "drive", "corpora": "allDrives", "pageSize": "10",
            "fields": "files(id,name,appProperties,description,webViewLink)",
            "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
        })
        result = self._request("GET", url)
        rows = result.get("files", [])
        if not isinstance(rows, list):
            raise ProviderProtocolError("Drive file list was malformed")
        if result.get("nextPageToken"):
            raise ProviderProtocolError("Drive query is paginated; refusing an incomplete uniqueness check")
        return rows

    def _metadata(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = event["payload"]
        name = str(payload.get("title") or payload.get("artifact_id") or "").strip()
        revision = str(payload.get("source_revision") or "").strip()
        if not name or not revision:
            raise ProviderProtocolError("Drive pointer requires title/artifact_id and source_revision")
        metadata: dict[str, Any] = {
            "name": name[:255],
            "appProperties": {
                "ixpansion_key": hashlib.sha256(event["idempotency_key"].encode("utf-8")).hexdigest(),
                "ixpansion_revision": hashlib.sha256(revision.encode("utf-8")).hexdigest(),
            },
            "description": f"IXPANSION artifact pointer; source revision: {revision[:500]}",
        }
        if self.parent_id:
            metadata["parents"] = [self.parent_id]
        url = payload.get("url")
        if url:
            if not str(url).startswith(("https://", "http://")):
                raise ProviderProtocolError("artifact url must be HTTP(S)")
            metadata["description"] += f"\nSource URL: {url}"
        mime_type = payload.get("mime_type")
        if mime_type:
            metadata["mimeType"] = str(mime_type)[:120]
        return metadata

    def deliver(self, event: dict[str, Any]) -> dict[str, Any]:
        metadata = self._metadata(event)
        matches = self._find(event)
        if len(matches) > 1:
            raise ProviderProtocolError("duplicate Drive files found for one idempotency key")
        fields = "id,name,appProperties,description,webViewLink"
        if matches:
            # Drive parent membership is changed only through explicit add/remove-parent
            # query parameters; this adapter never moves an existing file.
            metadata.pop("parents", None)
            metadata.pop("mimeType", None)
            file_id = matches[0].get("id")
            if not file_id:
                raise ProviderProtocolError("Drive query result omitted file id")
            query = urllib.parse.urlencode({"fields": fields, "supportsAllDrives": "true"})
            result = self._request(
                "PATCH", f"https://www.googleapis.com/drive/v3/files/{urllib.parse.quote(file_id, safe='')}?{query}",
                metadata,
            )
        else:
            query = urllib.parse.urlencode({"fields": fields, "supportsAllDrives": "true"})
            result = self._request("POST", f"https://www.googleapis.com/drive/v3/files?{query}", metadata)
        file_id = result.get("id")
        if not file_id:
            raise ProviderProtocolError("Drive write response omitted file id")
        return {"file_id": file_id, "idempotency_key": event["idempotency_key"],
                "source_revision": str(event["payload"]["source_revision"])}

    def verify(self, event: dict[str, Any], receipt: dict[str, Any]) -> bool:
        file_id = receipt.get("file_id")
        if not file_id:
            return False
        query = urllib.parse.urlencode({
            "fields": "id,name,appProperties,description,webViewLink",
            "supportsAllDrives": "true",
        })
        file = self._request(
            "GET", f"https://www.googleapis.com/drive/v3/files/{urllib.parse.quote(str(file_id), safe='')}?{query}",
        )
        props = file.get("appProperties", {})
        expected_name = str(event["payload"].get("title") or event["payload"].get("artifact_id") or "").strip()
        return (
            file.get("id") == file_id
            and file.get("name") == expected_name[:255]
            and props.get("ixpansion_key") == hashlib.sha256(event["idempotency_key"].encode("utf-8")).hexdigest()
            and props.get("ixpansion_revision") == hashlib.sha256(str(event["payload"]["source_revision"]).encode("utf-8")).hexdigest()
            and (
                not event["payload"].get("url")
                or str(event["payload"]["url"]) in str(file.get("description", ""))
            )
        )
