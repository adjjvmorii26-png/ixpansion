"""Runtime Vault — atomic, environment-overridable state for Chrono Forge."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / ".runtime" / "lab"


def root() -> Path:
    configured = os.environ.get("NEXUS_LAB_RUNTIME")
    return Path(configured).resolve() if configured else DEFAULT_ROOT.resolve()


def path(*parts: str) -> Path:
    boundary = root()
    target = boundary.joinpath(*parts).resolve()
    if not target.is_relative_to(boundary):
        raise ValueError("runtime path escapes the vault")
    return target


def state_path(*parts: str) -> Path:
    return path("state", *parts)


def ledger_path(name: str = "proof.jsonl") -> Path:
    return path("ledgers", name)


def report_path(name: str) -> Path:
    return path("reports", name)


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, payload: Any) -> None:
    """Replace JSON atomically so readers never observe a partial ritual."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    records = []
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one complete record under an exclusive process lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return record


ZERO_HASH = "0" * 64
CHAIN_FIELDS = {"sequence", "previous_hash", "entry_hash"}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _entry_hash(sequence: int, previous_hash: str, record: dict[str, Any]) -> str:
    payload = {"data": record, "previous_hash": previous_hash, "sequence": sequence}
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _raw_records(path: Path) -> list[tuple[int, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    parsed = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            parsed.append((number, json.loads(line)))
        except json.JSONDecodeError as error:
            parsed.append((number, f"__invalid_json__:{error}"))
    return parsed


def append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one hash-chained record under an exclusive process lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        previous_record = None
        for line in handle:
            if not line.strip():
                continue
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict):
                previous_record = candidate
        if previous_record and CHAIN_FIELDS.issubset(previous_record):
            sequence = int(previous_record["sequence"]) + 1
            previous_hash = str(previous_record["entry_hash"])
        else:
            sequence = 1
            previous_hash = ZERO_HASH
        data = dict(record)
        sealed = {
            **data,
            "sequence": sequence,
            "previous_hash": previous_hash,
            "entry_hash": _entry_hash(sequence, previous_hash, data),
        }
        handle.write(json.dumps(sealed, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return sealed


def verify_jsonl(path: Path) -> dict[str, Any]:
    """Audit a ledger, accepting legacy records only before the first chain."""
    raw = _raw_records(path)
    records: list[dict[str, Any]] = []
    failure = None
    legacy_count = 0
    chained_count = 0
    segments = 0
    expected_sequence = 1
    previous_hash = ZERO_HASH
    saw_chain = False

    for line_number, value in raw:
        if not isinstance(value, dict):
            failure = {"kind": "invalid_json", "line": line_number,
                       "detail": value.get("__error__", "") if isinstance(value, dict) else ""}
            break
        if not CHAIN_FIELDS.issubset(value):
            if saw_chain:
                failure = {"kind": "legacy_after_chain", "line": line_number}
                break
            legacy_count += 1
            records.append(value)
            continue

        data = {key: item for key, item in value.items() if key not in CHAIN_FIELDS}
        valid_sequence = int(value["sequence"]) == expected_sequence
        valid_link = str(value["previous_hash"]) == previous_hash
        valid_hash = str(value["entry_hash"]) == _entry_hash(expected_sequence, previous_hash, data)
        if not valid_sequence or not valid_link or not valid_hash:
            failure = {
                "kind": "chain_mismatch",
                "line": line_number,
                "sequence": value.get("sequence"),
                "expected_sequence": expected_sequence,
                "link_valid": valid_link,
                "hash_valid": valid_hash,
            }
            break
        if not saw_chain or expected_sequence == 1:
            segments += 1
        saw_chain = True
        chained_count += 1
        records.append(value)
        previous_hash = str(value["entry_hash"])
        expected_sequence += 1

    return {
        "schema": "aleph.runtime.ledger.audit.v1",
        "ok": failure is None,
        "records": len(records),
        "legacy_records": legacy_count,
        "chained_records": chained_count,
        "segments": segments,
        "failure": failure,
        "tail_hash": previous_hash if saw_chain else "",
    }
