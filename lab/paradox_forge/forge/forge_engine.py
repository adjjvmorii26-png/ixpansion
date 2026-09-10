#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def status() -> dict:
    core = (HERE / "forge_core.frg").read_text().strip() if (HERE / "forge_core.frg").exists() else None
    mut = json.loads((HERE / "forge_mutations.map").read_text()) if (HERE / "forge_mutations.map").exists() else {}
    return {"core": core, "mutations": mut}
if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
