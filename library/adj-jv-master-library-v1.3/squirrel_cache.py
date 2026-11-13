"""Integrity-aware local cache for small, tagged knowledge snippets.

The cache is a convenience store, not an evidence verifier: a valid digest proves
that cached bytes have not changed relative to the manifest, not that a snippet
is true.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
_TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_MANIFEST_NAME = "cache_manifest.json"
_LOCK = threading.RLock()


class CacheIntegrityError(ValueError):
    """Raised when cache metadata or cached content fails integrity checks."""


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class SquirrelCache:
    """Store and retrieve tagged snippets under a dedicated cache directory."""

    def __init__(self, cache_dir: str | Path = Path("cache") / "nuts") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.cache_dir / _MANIFEST_NAME

    @staticmethod
    def _validate_tag(tag: str) -> None:
        if not isinstance(tag, str) or not _TAG_RE.fullmatch(tag):
            raise ValueError("tag must be 1-64 safe characters: letters, digits, '.', '_' or '-'")

    def _read_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"schema_version": SCHEMA_VERSION, "entries": []}
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CacheIntegrityError(f"cannot read cache manifest: {exc}") from exc

        # Migrate the original demo's list-shaped manifest without trusting paths.
        if isinstance(data, list):
            migrated: list[dict[str, Any]] = []
            for old in data:
                if not isinstance(old, dict):
                    raise CacheIntegrityError("legacy manifest entries must be objects")
                tag, filename = old.get("tag"), old.get("file")
                if not isinstance(tag, str) or not isinstance(filename, str) or Path(filename).name != filename:
                    raise CacheIntegrityError("invalid legacy manifest entry")
                path = self.cache_dir / filename
                try:
                    raw = path.read_bytes()
                    nut = json.loads(raw.decode("utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise CacheIntegrityError(f"cannot migrate legacy cache item {filename}: {exc}") from exc
                if not _TAG_RE.fullmatch(tag) or not filename.endswith(".json"):
                    raise CacheIntegrityError(f"invalid legacy tag or filename: {filename}")
                if nut.get("tag") != tag or not isinstance(nut.get("snippet"), str):
                    raise CacheIntegrityError(f"legacy cache item does not match manifest: {filename}")
                # Upgrade the cached record itself to the v1 shape before hashing it.
                # Otherwise the new reader would correctly reject its missing stable ID.
                entry_id = str(uuid.uuid4())
                cached_at = nut.get("cached_at", 0)
                if not isinstance(cached_at, int) or isinstance(cached_at, bool) or cached_at < 0:
                    cached_at = 0
                upgraded = {
                    "id": entry_id, "tag": tag,
                    "snippet": nut["snippet"], "cached_at": cached_at,
                }
                upgraded_raw = _canonical_json(upgraded)
                _atomic_write(path, upgraded_raw)
                migrated.append({
                    "id": entry_id, "tag": tag, "file": filename,
                    "sha256": _sha256(upgraded_raw), "cached_at": cached_at,
                })
            result = {"schema_version": SCHEMA_VERSION, "entries": migrated}
            self._write_manifest(result)
            return result

        if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("entries"), list):
            raise CacheIntegrityError("unsupported or malformed cache manifest")
        seen_ids: set[str] = set()
        seen_files: set[str] = set()
        for entry in data["entries"]:
            if not isinstance(entry, dict):
                raise CacheIntegrityError("manifest entries must be objects")
            entry_id, tag, filename, digest = (entry.get(k) for k in ("id", "tag", "file", "sha256"))
            if not isinstance(entry_id, str) or not entry_id or entry_id in seen_ids:
                raise CacheIntegrityError("manifest contains missing or duplicate entry IDs")
            if not isinstance(tag, str) or not _TAG_RE.fullmatch(tag):
                raise CacheIntegrityError(f"invalid tag in manifest entry {entry_id}")
            if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".json"):
                raise CacheIntegrityError(f"unsafe filename in manifest entry {entry_id}")
            if filename in seen_files:
                raise CacheIntegrityError(f"duplicate filename in manifest: {filename}")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise CacheIntegrityError(f"invalid SHA-256 digest in manifest entry {entry_id}")
            seen_ids.add(entry_id)
            seen_files.add(filename)
        return data

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        _atomic_write(self.manifest_path, _canonical_json(manifest))

    def hoard(self, tag: str, snippet: str) -> str:
        """Atomically store a snippet and return its stable cache entry ID."""
        self._validate_tag(tag)
        if not isinstance(snippet, str) or not snippet.strip():
            raise ValueError("snippet must be a non-empty string")
        with _LOCK:
            manifest = self._read_manifest()
            entry_id = str(uuid.uuid4())
            filename = f"nut_{entry_id}.json"
            cached_at = int(time.time())
            payload = {"id": entry_id, "tag": tag, "snippet": snippet, "cached_at": cached_at}
            raw = _canonical_json(payload)
            target = self.cache_dir / filename
            _atomic_write(target, raw)
            manifest["entries"].append({
                "id": entry_id, "tag": tag, "file": filename,
                "sha256": _sha256(raw), "cached_at": cached_at,
            })
            try:
                self._write_manifest(manifest)
            except BaseException:
                target.unlink(missing_ok=True)
                raise
            print(f"🐿️ [Squirrel Collector] Hoarded '{tag}' -> {filename}")
            return entry_id

    def retrieve(self, tag: str) -> list[str]:
        """Return matching snippets, rejecting missing or modified cache files."""
        self._validate_tag(tag)
        with _LOCK:
            manifest = self._read_manifest()
            results: list[str] = []
            for entry in manifest["entries"]:
                if entry["tag"] != tag:
                    continue
                target = self.cache_dir / entry["file"]
                try:
                    raw = target.read_bytes()
                except OSError as exc:
                    raise CacheIntegrityError(f"missing cache item {entry['file']}") from exc
                if _sha256(raw) != entry["sha256"]:
                    raise CacheIntegrityError(f"SHA-256 mismatch for {entry['file']}")
                try:
                    nut = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise CacheIntegrityError(f"invalid JSON in {entry['file']}") from exc
                if nut.get("id") != entry["id"] or nut.get("tag") != entry["tag"] or not isinstance(nut.get("snippet"), str):
                    raise CacheIntegrityError(f"cache content does not match manifest for {entry['file']}")
                results.append(nut["snippet"])
            print(f"🐾 [Nut Retrieval] Retrieved {len(results)} nut(s) for tag: '{tag}'")
            return results


_DEFAULT_CACHE: SquirrelCache | None = None


def _default_cache() -> SquirrelCache:
    # Lazy initialization avoids creating cache directories just by importing this module.
    global _DEFAULT_CACHE
    if _DEFAULT_CACHE is None:
        _DEFAULT_CACHE = SquirrelCache()
    return _DEFAULT_CACHE


def squirrel_hoard(tag: str, snippet: str) -> str:
    """Compatibility wrapper for the original demo function."""
    return _default_cache().hoard(tag, snippet)


def squirrel_retrieve(tag: str) -> list[str]:
    """Compatibility wrapper for the original demo function."""
    return _default_cache().retrieve(tag)


if __name__ == "__main__":
    squirrel_hoard("sqlite_trick", "Use DatabaseSync from node:sqlite for synchronous zero-dep transactions.")
    squirrel_hoard("dark_hex", "Background: #03040A, Accents: #00E5FF & #FF2BD6.")
    print("\n--- WINTER RETRIEVAL PASS ---")
    print(squirrel_retrieve("dark_hex"))
