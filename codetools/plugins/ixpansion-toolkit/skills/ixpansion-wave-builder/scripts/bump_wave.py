#!/usr/bin/env python3
"""Bump the IXpansion version + wave across all canonical files.

Usage:
  python3 bump_wave.py --version 4.03.0 --wave 215 --name "The Organism Teaches"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

def _resolve_root() -> Path:
    """Use CWD when it looks like the IXpansion repo; else walk up from this file."""
    cwd = Path.cwd()
    if (cwd / "api_server.py").exists():
        return cwd
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "api_server.py").exists():
            return parent
    return here.parents[2]

ROOT = _resolve_root()

FILES = [
    (ROOT / "api_server.py", [
        (r'VERSION = "[0-9.]+"', 'VERSION = "{version}"'),
        (r'WAVE = "[0-9]+"', 'WAVE = "{wave}"'),
        (r'WAVE_NAME = "[^"]+"', 'WAVE_NAME = "{name}"'),
    ]),
    (ROOT / "api" / "organism_ontology.py", [
        (r'ORGANISM_VERSION = "[0-9.]+"', 'ORGANISM_VERSION = "{version}"'),
        (r'ORGANISM_WAVE = [0-9]+', 'ORGANISM_WAVE = {wave_int}'),
        (r'ORGANISM_WAVE_NAME = "[^"]+"', 'ORGANISM_WAVE_NAME = "{name}"'),
    ]),
    (ROOT / "dashboard" / "shared.js", [
        (r'version: "[0-9.]+"', 'version: "{version}"'),
        (r'wave: [0-9]+', 'wave: {wave_int}'),
        (r'waveName: "[^"]+"', 'waveName: "{name}"'),
    ]),
    (ROOT / "pyproject.toml", [
        (r'version = "[0-9.]+"', 'version = "{version}"'),
    ]),
    (ROOT / "CITATION.cff", [
        (r'version: "[0-9.]+"', 'version: "{version}"'),
    ]),
    (ROOT / "README.md", [
        (r'\*\*Version:\*\* [0-9.]+', '**Version:** {version}'),
    ]),
]


def bump(version: str, wave: int, name: str) -> list:
    changed = []
    for path, rules in FILES:
        if not path.exists():
            continue
        src = path.read_text()
        original = src
        for pattern, replacement in rules:
            if "wave_int" in replacement:
                replacement = replacement.replace("{wave_int}", str(wave))
            src = re.sub(pattern, replacement.format(version=version, wave=wave, name=name), src)
        if src != original:
            path.write_text(src)
            changed.append(str(path))
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump IXpansion version/wave")
    parser.add_argument("--version", required=True)
    parser.add_argument("--wave", type=int, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    changed = bump(args.version, args.wave, args.name)
    if not changed:
        sys.exit("error: no files updated (paths exist?)")
    print("[OK] bumped in:")
    for c in changed:
        print(f"  {c}")


if __name__ == "__main__":
    main()
