#!/usr/bin/env python3
"""Scaffold a new living organ for IXpansion.

Usage:
  python3 scaffold_organ.py <name> [--layer <layer>] [--resonance 0.6]
  python3 scaffold_organ.py my_organ --wave 215 --layer immortal

Writes api/<name>.py with the canonical boilerplate.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEMPLATE_LINES = [
    "\"\"\"Wave {wave} - {title}.",
    "",
    "{{TODO: one-paragraph description of what this organ does and why it exists.}}",
    "\"\"\"",
    "from __future__ import annotations",
    "",
    "from typing import Any, Dict",
    "",
    "",
    "def coherence_vitals() -> Dict[str, Any]:",
    "    return {{",
    "        \"layer\": \"{layer}\",",
    "        \"status\": \"stable\",",
    "        \"resonance\": {resonance},",
    "        \"wave\": {wave},",
    "    }}",
    "",
    "",
    "def resonates_with() -> list:",
    "    return [{kinships}]",
    "",
    "",
    "def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:",
    "    payload = payload or {{}}",
    "    context = context or {{}}",
    "    # TODO: implement",
    "    return {{\"status\": \"active\", \"module\": \"{name}\"}}",
    "",
]
TEMPLATE = chr(10).join(TEMPLATE_LINES)


def main():
    parser = argparse.ArgumentParser(description="Scaffold an IXpansion organ")
    parser.add_argument("name")
    parser.add_argument("--layer", default="emergent")
    parser.add_argument("--resonance", type=float, default=0.6)
    parser.add_argument("--wave", type=int, default=214)
    parser.add_argument("--out", default="api")
    args = parser.parse_args()

    name = args.name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name).strip("_")
    if not name:
        sys.exit("error: name must contain letters/digits")
    title = " ".join(w.capitalize() for w in name.split("_"))
    parts = [p for p in name.split('_') if len(p) > 2]
    kinship = ", ".join('"' + p + '"' for p in parts[:3]) or '"self"'
    path = Path(args.out) / f"{name}.py"
    if path.exists():
        sys.exit(f"error: {path} already exists")
    path.write_text(TEMPLATE.format(wave=args.wave, title=title, layer=args.layer,
                                    resonance=args.resonance, name=name, kinships=kinship))
    print(f"[OK] scaffolded {path}")

if __name__ == "__main__":
    main()
