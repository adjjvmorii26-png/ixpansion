#!/usr/bin/env python3
"""Constellation Caption — generate natural language from graph layouts."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import read_json, state_path, write_json

SCHEMA = "aleph.experiments.constellation-caption.v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "caption_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _angle_label(angle: float) -> str:
    deg = math.degrees(angle) % 360
    labels = [
        (0, "3 o'clock"), (45, "2 o'clock"), (90, "12 o'clock"),
        (135, "10 o'clock"), (180, "9 o'clock"), (225, "7 o'clock"),
        (270, "6 o'clock"), (315, "5 o'clock"), (360, "3 o'clock"),
    ]
    best = min(labels, key=lambda x: abs(x[0] - deg))
    return best[1]


def _distance_label(dist: float) -> str:
    if dist < 0.2:
        return "tightly clustered"
    elif dist < 0.5:
        return "moderately spaced"
    elif dist < 0.8:
        return "widely distributed"
    else:
        return "at the periphery"


def describe_constellation(
    nodes: list[dict[str, Any]],
    *,
    center: tuple[float, float] = (0.5, 0.5),
    clock: Any = utc_now,
) -> dict[str, Any]:
    """Generate a natural-language description of a constellation layout."""
    captions = []
    for node in nodes:
        x = float(node.get("x", 0.5))
        y = float(node.get("y", 0.5))
        dx = x - center[0]
        dy = y - center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(-dy, dx)
        node_id = node.get("id", "unknown")
        sigil = node.get("sigil", "·")
        weight = float(node.get("weight", 1.0))

        position = _angle_label(angle)
        spread = _distance_label(dist)
        if weight > 1.5:
            emphasis = "prominent"
        elif weight < 0.5:
            emphasis = "subtle"
        else:
            emphasis = "balanced"

        caption = f"{node_id} ({sigil}) sits at {position}, {spread} from center, with {emphasis} weight."
        captions.append(caption)

    if len(nodes) >= 2:
        dx = float(nodes[0].get("x", 0.5)) - float(nodes[1].get("x", 0.5))
        dy = float(nodes[0].get("y", 0.5)) - float(nodes[1].get("y", 0.5))
        span = math.sqrt(dx * dx + dy * dy)
        summary = f"The constellation spans {len(nodes)} nodes across a {span:.2f}-unit radius."
    else:
        summary = f"The constellation contains {len(nodes)} solitary node."

    description = f"{summary} {' '.join(captions)}"

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "constellation-caption",
        "sealed_at": clock(),
        "node_count": len(nodes),
        "captions": captions,
        "summary": summary,
        "description": description,
        "execution_enabled": False,
    }
    result["caption_hash"] = _hash(result)
    return result


def generate_caption(
    nodes: list[dict[str, Any]],
    *,
    clock: Any = utc_now,
    record: bool = True,
) -> dict[str, Any]:
    """Generate and optionally persist a constellation caption."""
    result = describe_constellation(nodes, clock=clock)
    if record:
        write_json(state_path("constellation", "caption.json"), result)
    return result


def main() -> int:
    data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
    result = generate_caption(data)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
