#!/usr/bin/env python3
"""Organism bridge — map GitHub limbs to organ roles."""
from __future__ import annotations
import json
from pathlib import Path

def load_organism(path: str | Path = "ORGANISM.json") -> dict:
    p = Path(path)
    if not p.exists():
        return {"name": "SOLID_ORGANISM", "limbs": [], "error": "missing"}
    return json.loads(p.read_text())

def by_role(role: str) -> list:
    return [L for L in load_organism().get("limbs", []) if L.get("role") == role]

def summary() -> dict:
    org = load_organism()
    roles = {}
    for L in org.get("limbs", []):
        roles.setdefault(L.get("role", "?"), []).append(L.get("name"))
    return {"organism": org.get("name"), "version": org.get("version"),
            "limb_count": len(org.get("limbs", [])), "roles": roles}

if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
