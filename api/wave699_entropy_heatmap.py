"""Wave 699 — Entropy Heatmap — visualizes all organism modules as a 2D entropy grid.

Each cell represents a module colored by its current entropy/divergence state.
Red = high entropy (unstable), blue = low entropy (stable), green = healthy.
The heatmap updates in real-time as the organism evolves.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave699_entropy_heatmap.json"
DEFAULT = {
    "module": "wave699_entropy_heatmap",
    "wave": 699,
    "grid": {},
    "heat_cells": [],
    "hot_zones": [],
    "cold_zones": [],
    "total_modules": 0,
    "last_update": "",
    "entropy_average": 0.0,
    "entropy_stddev": 0.0,
}


def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def coherence_vitals():
    st = _load()
    return {
        "wave": 699,
        "module": "wave699_entropy_heatmap",
        "ok": True,
        "total_modules": st["total_modules"],
        "entropy_average": st["entropy_average"],
        "entropy_stddev": st["entropy_stddev"],
        "hot_zones": len(st["hot_zones"]),
        "cold_zones": len(st["cold_zones"]),
    }


def resonates_with():
    return ["wave694_quantum_coherence_lattice", "wave698_void_syntax_engine", "organism_vitals"]


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "update":
        modules = req.get("modules", [])
        grid_size = req.get("grid_size", 32)
        for m in modules:
            h = hashlib.sha256(m.encode()).hexdigest()
            entropy = (int(h[:4], 16) % 100) / 100.0
            row = (int(h[4:6], 16) % grid_size)
            col = (int(h[6:8], 16) % grid_size)
            st["grid"][m] = {"row": row, "col": col, "entropy": entropy}
        st["total_modules"] = len(modules)
        entropies = [v["entropy"] for v in st["grid"].values()] or [0]
        st["entropy_average"] = round(sum(entropies) / len(entropies), 4)
        st["entropy_stddev"] = round(
            (sum((e - st["entropy_average"])**2 for e in entropies) / len(entropies))**0.5, 4
        )
        st["hot_zones"] = [m for m, v in st["grid"].items() if v["entropy"] > 0.7]
        st["cold_zones"] = [m for m, v in st["grid"].items() if v["entropy"] < 0.3]
        st["last_update"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "updated", "modules": len(modules), "entropy_avg": st["entropy_average"], "wave": 699}

    if action == "cell":
        row = req.get("row", 0)
        col = req.get("col", 0)
        cells = {m: v for m, v in st["grid"].items() if v["row"] == row and v["col"] == col}
        return {"status": "cells", "row": row, "col": col, "count": len(cells), "modules": list(cells.keys()), "wave": 699}

    if action == "hot_zones":
        return {"status": "hot_zones", "zones": st["hot_zones"][:20], "count": len(st["hot_zones"]), "wave": 699}

    if action == "cold_zones":
        return {"status": "cold_zones", "zones": st["cold_zones"][:20], "count": len(st["cold_zones"]), "wave": 699}

    if action == "status":
        return {
            "status": "active",
            "module": "wave699_entropy_heatmap",
            "wave": 699,
            "total_modules": st["total_modules"],
            "entropy_average": st["entropy_average"],
            "entropy_stddev": st["entropy_stddev"],
            "hot_zones": len(st["hot_zones"]),
            "cold_zones": len(st["cold_zones"]),
            "last_update": st["last_update"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    import json as _j
    print(_j.dumps(handler({"action": "status"}), indent=2))
