#!/usr/bin/env python3
"""Sync VERSION / WAVE / narrative across all IXPANSION release metadata.

Usage:
    python3 scripts/bump_versions.py --version 4.112.0 --wave 752 --name "Gene Splicer"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "api_server.py",                    # VERSION / WAVE / WAVE_NAME
    "api/organism_ontology.py",         # VERSION / ORGANISM_VERSION / ORGANISM_WAVE / ORGANISM_WAVE_NAME
    "dashboard/shared.js",              # version / wave / waveName
    "pyproject.toml",                   # version
    "CITATION.cff",                     # version
]


def bump(fname: str, version: str, wave: str, wave_name: str) -> bool:
    path = ROOT / fname
    if not path.exists():
        print(f"  skip {fname} (missing)")
        return False
    text = path.read_text()
    changed = False

    if fname == "api_server.py":
        text = re.sub(r'^VERSION\s*=.*$', f'VERSION = "{version}"', text, flags=re.M)
        text = re.sub(r'^WAVE\s*=.*$', f'WAVE = "{wave}"', text, flags=re.M)
        text = re.sub(r'^WAVE_NAME\s*=.*$', f'WAVE_NAME = "{wave_name} — how the organism evolves"', text, flags=re.M)
        changed = True

    elif fname == "api/organism_ontology.py":
        text = re.sub(r'^VERSION\s*=.*$', f'VERSION = "{version}"', text, flags=re.M)
        text = re.sub(r'^ORGANISM_VERSION\s*=.*$', f'ORGANISM_VERSION = "{version}"', text, flags=re.M)
        text = re.sub(r'^ORGANISM_WAVE\s*=.*$', f'ORGANISM_WAVE = {int(wave)}', text, flags=re.M)
        text = re.sub(r'^ORGANISM_WAVE_NAME\s*=.*$', f'ORGANISM_WAVE_NAME = "{wave_name} — how the organism evolves"', text, flags=re.M)
        changed = True

    elif fname == "dashboard/shared.js":
        text = re.sub(r'"version":\s*"[^"]+"', f'"version": "{version}"', text)
        text = re.sub(r'wave:\s*\d+', f'wave: {int(wave)}', text)
        text = re.sub(r'waveName:\s*"[^"]+"', f'waveName: "{wave_name}"', text)
        changed = True

    elif fname == "pyproject.toml":
        text = re.sub(r'^version\s*=\s*".*"$', f'version = "{version}"', text, flags=re.M)
        changed = True

    elif fname == "CITATION.cff":
        text = re.sub(r'^version:\s*".*"$', f'version: "{version}"', text, flags=re.M)
        changed = True

    path.write_text(text)
    print(f"  synced {fname}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync IXPANSION release metadata")
    parser.add_argument("--version", required=True)
    parser.add_argument("--wave", required=True, type=int)
    parser.add_argument("--name", required=True, help="wave name, e.g. 'Gene Splicer'")
    args = parser.parse_args()

    for fname in FILES:
        bump(fname, args.version, str(args.wave), args.name)

    print(f"\nDone: v{args.version} · Wave {args.wave} · {args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
