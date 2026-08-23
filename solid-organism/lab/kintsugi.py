#!/usr/bin/env python3
"""Kintsugi repair: strengthen broken artifacts without erasing their scars."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def repair(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return a repaired copy where every crack becomes a first-class golden seam."""
    if "id" not in artifact or not isinstance(artifact["fractures"], list):
        raise ValueError("artifact requires id and fractures")

    repaired = {**artifact, "state": "repaired", "seams": []}
    for index, fracture in enumerate(artifact["fractures"]):
        fingerprint = _digest({"artifact": artifact["id"], "fracture": fracture})
        repaired["seams"].append({
            "index": index,
            "source_fracture": fracture.get("id", index),
            "gold_alloy": f"au:{fingerprint[:12]}",
            "tensile_gift": round(0.72 + (int(fingerprint[:2], 16) / 255) * 0.27, 3),
            "scar_visibility": "honored",
        })
    repaired["repair_fingerprint"] = _digest({
        "id": artifact["id"], "fractures": artifact["fractures"]
    })
    return repaired


def demo() -> dict[str, Any]:
    return repair({
        "id": "vessel-of-becoming",
        "material": " fired clay ".strip(),
        "fractures": [
            {"id": "old-certainty", "length": 7},
            {"id": "borrowed-shape", "length": 4},
        ],
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repair a broken artifact with golden seams")
    parser.add_argument("--artifact", type=Path, help="JSON artifact; omit for the demo vessel")
    args = parser.parse_args(argv)
    try:
        raw = args.artifact.read_text(encoding="utf-8") if args.artifact else None
        result = repair(json.loads(raw)) if raw is not None else demo()
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
