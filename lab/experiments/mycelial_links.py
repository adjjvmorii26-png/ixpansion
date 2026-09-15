#!/usr/bin/env python3
"""Mycelial Links — shared name tokens between lab experiment files."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def tokens(name: str):
    return set(re.findall(r"[a-z]+", name.replace(".py", "").lower()))
def main():
    exp = REPO / "lab" / "experiments"
    files = list(exp.glob("*.py")) if exp.exists() else []
    tok_map = {p.name: tokens(p.name) for p in files}
    names = list(tok_map.keys())
    links = []
    for i, a in enumerate(names):
        for b in names[i+1:]:
            shared = tok_map[a] & tok_map[b]
            if len(shared) >= 2:
                links.append({"a": a, "b": b, "shared": sorted(shared)})
    links = links[:15]
    frames = [{"t": "0.0s", "role": "hook", "text": "MYCELIAL LINKS", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(links)} hyphae", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": (links[0]["a"][:20] if links else "sparse"), "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · names that share root", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "mycelial_links", "files": len(files), "links": links, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
