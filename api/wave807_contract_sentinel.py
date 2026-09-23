"""Wave 807 — contract sentinel.

Consumes the Wave 806 static registry and reports contract completeness
without importing organs. Silence is the product surface.
"""
from __future__ import annotations

from typing import Any

WAVE = 807
NAME = "contract_sentinel"
REQUIRED = ("handler", "coherence_vitals", "resonates_with")


def _registry_snapshot() -> dict[str, Any]:
    from wave806_organ_registry import registry

    return registry()


def evaluate(snap: dict[str, Any] | None = None) -> dict[str, Any]:
    snap = snap or _registry_snapshot()
    organs = [o for o in snap.get("organs", []) if o.get("valid")]
    gaps = []
    for organ in organs:
        contract = organ.get("contract") or {}
        missing = [key for key in REQUIRED if not contract.get(key)]
        if missing:
            gaps.append({"name": organ.get("name"), "missing": missing})
    invalid = [o.get("name") for o in snap.get("organs", []) if not o.get("valid")]
    ok = len(gaps) == 0 and len(invalid) == 0
    return {
        "wave": WAVE,
        "name": NAME,
        "ok": ok,
        "total": snap.get("total", 0),
        "valid": snap.get("valid", 0),
        "invalid": invalid,
        "gaps": gaps,
        "gap_count": len(gaps),
        "stateful": snap.get("stateful", 0),
        "audio": False,
    }


def coherence_vitals() -> dict[str, Any]:
    verdict = evaluate()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave807_contract_sentinel",
        "ok": verdict["ok"],
        "layer": "meta",
        "status": "clear" if verdict["ok"] else "gaps",
        "gap_count": verdict["gap_count"],
        "invalid_count": len(verdict["invalid"]),
        "surface": "sentinel",
        "audio": False,
    }


def resonates_with() -> list[str]:
    return [
        "wave806_organ_registry",
        "coherence_validator",
        "organism_genome",
    ]


def handler(req=None) -> dict[str, Any]:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    if action in {"scan", "evaluate", "gaps"}:
        return evaluate()
    return {**coherence_vitals(), "action": action if action != "status" else "status"}


if __name__ == "__main__":
    import json

    print(json.dumps(handler({"action": "status"}), indent=2))
