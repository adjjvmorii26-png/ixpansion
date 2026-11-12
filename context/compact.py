"""IXPANSION compact context packer.

Typed artifacts only. No network, no secrets, no chat dumps.
Agents load pack(budget_tokens), never full history.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

KINDS = frozenset({"pulse", "receipt", "seed", "residue", "contract", "pointer"})
DEFAULT_TTL = {
    "pulse": 7,
    "receipt": 90,
    "seed": 0,
    "residue": 180,
    "contract": 0,
    "pointer": 30,
}
CHARS_PER_TOKEN = 4
# Raw controls (except tab/LF/CR) break strict JSON; sanitize before loads.
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class ArtifactError(ValueError):
    pass


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_day(t: str) -> date:
    return date.fromisoformat((t or "")[:10])


def validate(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ArtifactError("record must be object")
    kind = record.get("kind")
    if kind not in KINDS:
        raise ArtifactError(f"invalid kind: {kind!r}")
    aid = record.get("id")
    if not isinstance(aid, str) or not aid.strip() or len(aid) > 128:
        raise ArtifactError("id required (1..128 chars)")
    if not isinstance(record.get("t"), str) or not record["t"]:
        raise ArtifactError("t required")
    body = record.get("body") or {}
    if not isinstance(body, dict):
        raise ArtifactError("body must be object")
    ttl = record.get("ttl_days", DEFAULT_TTL[kind])
    if not isinstance(ttl, int) or ttl < 0:
        raise ArtifactError("ttl_days must be int >= 0")
    refs = record.get("refs") or []
    if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
        raise ArtifactError("refs must be string list")
    out = {
        "kind": kind,
        "id": aid.strip(),
        "t": record["t"],
        "body": body,
        "ttl_days": ttl,
        "refs": list(refs),
    }
    if record.get("sha"):
        out["sha"] = str(record["sha"])
    return out


def canonical_bytes(record: dict[str, Any]) -> bytes:
    r = validate(record)
    payload = {"kind": r["kind"], "id": r["id"], "body": r["body"], "sha": r.get("sha")}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def content_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()[:16]


def is_expired(record: dict[str, Any], today: date | None = None) -> bool:
    r = validate(record)
    if r["ttl_days"] == 0:
        return False
    return ((_today() if today is None else today) - _parse_day(r["t"])).days > r["ttl_days"]


def forget(
    records: Iterable[dict[str, Any]],
    *,
    today: date | None = None,
    drop_kinds: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Drop expired records and optionally whole kinds."""
    drop = frozenset(drop_kinds or ())
    out: list[dict[str, Any]] = []
    for raw in records:
        r = validate(raw)
        if r["kind"] in drop or is_expired(r, today=today):
            continue
        out.append(r)
    return out


def bind(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse exact duplicates; fail if same id different body."""
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for raw in records:
        r = validate(raw)
        aid = r["id"]
        h = content_hash(r)
        if aid not in by_id:
            by_id[aid] = r
            by_id[aid]["_h"] = h
            order.append(aid)
            continue
        if by_id[aid]["_h"] != h:
            raise ArtifactError(f"id conflict: {aid}")
    out = []
    for aid in order:
        r = dict(by_id[aid])
        r.pop("_h", None)
        out.append(r)
    return out


def promote_residue_to_seed(
    residue: dict[str, Any], *,
    seed_id: str | None = None,
) -> dict[str, Any]:
    """Turn a lesson into a permanent seed."""
    r = validate(residue)
    if r["kind"] != "residue":
        raise ArtifactError("promote requires kind=residue")
    lesson = r["body"].get("lesson") or r["body"].get("fail") or ""
    if not lesson:
        raise ArtifactError("residue needs lesson or fail")
    return validate({
        "kind": "seed",
        "id": seed_id or f"seed:{r['id']}",
        "t": r["t"],
        "ttl_days": 0,
        "body": {"intent": str(lesson)[:240], "from": r["id"]},
        "refs": [r["id"]],
    })


def to_line(r: dict[str, Any]) -> str:
    r = validate(r)
    parts = [r["kind"], r["t"][:10], r["id"]]
    if r.get("sha"):
        parts.append(r["sha"][:12])
    for k in sorted((r.get("body") or {}).keys()):
        v = r["body"][k]
        if v is None:
            continue
        s = str(v).replace("|", "/").replace("\n", " ")
        if len(s) > 80:
            s = s[:77] + "..."
        parts.append(f"{k}={s}")
    return "|".join(parts)


def pack(
    records: Iterable[dict[str, Any]],
    *,
    budget_tokens: int = 3000,
    today: date | None = None,
    priority: tuple[str, ...] = ("seed", "contract", "receipt", "pulse", "pointer", "residue"),
) -> str:
    """Return a budget-limited text pack for agent context."""
    if budget_tokens < 64:
        raise ArtifactError("budget_tokens too small")
    cleaned = bind(forget(records, today=today))
    rank = {k: i for i, k in enumerate(priority)}
    cleaned.sort(key=lambda r: (rank.get(r["kind"], 99), r["t"], r["id"]))
    budget_chars = budget_tokens * CHARS_PER_TOKEN
    lines: list[str] = []
    used = 0
    for r in cleaned:
        line = to_line(r)
        cost = len(line) + 1
        if used + cost > budget_chars:
            break
        lines.append(line)
        used += cost
    header = f"# ixpansion-context pack tokens~{used // CHARS_PER_TOKEN}/{budget_tokens} n={len(lines)}"
    return header + "\n" + "\n".join(lines) + ("\n" if lines else "")


def load_jsonl(path: Path | str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Tolerate accidental raw control chars in historical ledger lines.
        safe = _CTRL_RE.sub(" ", line)
        out.append(validate(json.loads(safe)))
    return out


def append_jsonl(path: Path | str, record: dict[str, Any]) -> dict[str, Any]:
    r = validate(record)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=True) + "\n")
    return r


def demo_pack() -> str:
    return pack(load_jsonl(Path(__file__).resolve().parent / "ledger.jsonl"), budget_tokens=800)


if __name__ == "__main__":
    print(demo_pack())
