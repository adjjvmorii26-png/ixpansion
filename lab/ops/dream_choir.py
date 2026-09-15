#!/usr/bin/env python3
"""Dream Choir — many Ouroboros dreams harmonized into one resonance map.

  python lab/ops/dream_choir.py --voices 5
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
DATA = ROOT / "data"
CONTENT = ROOT / "content_output" / "kernel_captions"
MAP_FILE = DATA / "dream_resonance_map.json"
MANIFEST = DATA / "dream_choir_manifest.json"

sys.path.insert(0, str(OPS))
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sing(voices: int = 5, *, force: bool = False) -> Dict[str, Any]:
    from ouroboros import cycle

    voices = max(1, min(int(voices), 16))
    t0 = time.perf_counter()
    dreams: List[Dict[str, Any]] = []
    for i in range(voices):
        r = cycle(scaffold=False, dream_only=True, force=force and i == 0)
        d = r.get("dream") or {}
        dreams.append({
            "voice": i + 1,
            "name": d.get("name"),
            "slug": d.get("slug"),
            "parts": d.get("parts") or [],
            "fp": (r.get("fingerprint") or "")[:16],
        })
        time.sleep(0.005)

    part_counts: Counter = Counter()
    for d in dreams:
        for p in d.get("parts") or []:
            part_counts[p] += 1

    edges: Counter = Counter()
    for d in dreams:
        parts = list(d.get("parts") or [])
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a, b = sorted([parts[i], parts[j]])
                edges[f"{a}|{b}"] += 1

    resonance = {
        "voices": len(dreams),
        "dreams": dreams,
        "part_frequency": dict(part_counts.most_common()),
        "edges": [
            {"a": k.split("|")[0], "b": k.split("|")[1], "weight": w}
            for k, w in edges.most_common()
        ],
        "dominant": [p for p, _ in part_counts.most_common(3)],
        "ts": _utc(),
    }

    DATA.mkdir(parents=True, exist_ok=True)
    try:
        MAP_FILE.write_text(json.dumps(resonance, indent=2) + "\n")
    except OSError:
        pass

    CONTENT.mkdir(parents=True, exist_ok=True)
    frames = [{"t": 0, "text": "DREAM CHOIR"}]
    t = 2
    for d in dreams[:8]:
        frames.append({"t": t, "text": str(d.get("name") or "…")})
        t += 2
    if resonance["dominant"]:
        frames.append({"t": t, "text": " · ".join(resonance["dominant"])})
        t += 2
    frames.append({"t": t, "text": "@CoodingLooop"})
    package = {
        "channel": "@CoodingLooop",
        "style": "silent_caption_only",
        "kind": "dream_choir",
        "frames": frames,
        "dominant": resonance["dominant"],
        "ts": _utc(),
    }
    cap_path = CONTENT / f"choir_{int(time.time())}.json"
    try:
        cap_path.write_text(json.dumps(package, indent=2) + "\n")
    except OSError:
        cap_path = None

    return {
        "status": "choir",
        "ok": True,
        "voices": voices,
        "resonance": resonance,
        "caption_path": str(cap_path.relative_to(ROOT)) if cap_path else None,
        "ms": round((time.perf_counter() - t0) * 1000, 2),
        "caption": "dream choir · many voices · one resonance map",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Dream Choir")
    p.add_argument("--voices", type=int, default=5)
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    m = sing(voices=args.voices, force=args.force)
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        MANIFEST.write_text(json.dumps(m, indent=2, default=str) + "\n")
    except OSError:
        pass
    print(json.dumps(m, indent=2, default=str))
    return 0 if m.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
