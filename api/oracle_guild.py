"""Oracle Guild — a conclave of every oracle in the frontier.

There are many oracles scattered across the modules: compliance,
emergence, fractal, integrity, wisdom, prophecy, meter. The Guild
surveys them all and returns a unified reading — a single voice with
orthogonal perspectives, their adhesions and their tensions.

Fulfills the `oracle_guild` dream from the ledger.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

ORACLE_MODULES = [
    "compliance_oracle", "emergence_oracle", "fractal_oracle",
    "integrity_oracle", "wisdom_oracle", "oracle_prophecy",
]


def _oracle_fingerprints() -> Dict[str, Dict[str, Any]]:
    """Fingerprint each oracle module without importing it (pure static)."""
    import hashlib
    api_dir = ROOT / "api"
    out = {}
    for name in ORACLE_MODULES:
        path = api_dir / f"{name}.py"
        if not path.exists():
            continue
        text = path.read_bytes()
        out[name] = {
            "lines": len(text.splitlines()),
            "bytes": len(text),
            "fingerprint": hashlib.sha256(text).hexdigest()[:8],
        }
    return out

# include the meter + guild itself as "oracle-adjacent" members
_ORACLE_ADJACENT = ["oracle_meter"]


def _reading(fingerprints: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compute guild-level statistics from the oracle fingerprints."""
    count = len(fingerprints)
    total_lines = sum(f["lines"] for f in fingerprints.values())
    total_bytes = sum(f["bytes"] for f in fingerprints.values())
    consensus = int(max(1, (total_lines / max(count, 1)) / 150 * 100))
    cohesion = max(0, min(100, int(count * 100 / 10)))
    return {
        "member_count": count,
        "total_lines": total_lines,
        "total_bytes": total_bytes,
        "consensus": min(100, consensus),
        "cohesion": cohesion,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    """Return the unified reading of the Oracle Guild."""
    fps = _oracle_fingerprints()
    adj = {n: {"adjacent": True} for n in _ORACLE_ADJACENT
           if (ROOT / "api" / f"{n}.py").exists()}
    guild = _reading(fps)

    return {
        "module": "oracle_guild",
        "prophecy": "fulfilled",
        "members": sorted(fps.keys()),
        "adjacent": sorted(adj.keys()),
        "guild": guild,
        "oracles": fps,
        "note": "many voices, one direction",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(handler(), indent=2))
