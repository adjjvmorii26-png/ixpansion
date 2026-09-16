"""Wave 730 — Catalog Registry.

Turns all 193 dashboards into a structured IXPANSION catalog
with descriptions, metadata, wave associations, and content.
"""
import json, hashlib, os, re
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave730_catalog_registry.json"
DASHBOARD_DIR = ROOT / "dashboard"
CATALOG_FILE = ROOT / "data" / "ixpansion_catalog.json"
WAVE = 730
NAME = "catalog_registry"

CATALOG_TEMPLATES = {
    "coherence": {"category": "Coherence", "icon": "🜂", "desc": "Measures organism coherence and resonance across waves."},
    "resonance": {"category": "Resonance", "icon": "🜁", "desc": "Tracks resonance chains and bridge connections."},
    "dream": {"category": "Dream", "icon": "🌙", "desc": "Dream logic and unconscious generation systems."},
    "glitch": {"category": "Glitch", "icon": "💀", "desc": "Paradox, divergence, and glitch pattern analysis."},
    "wave": {"category": "Wave", "icon": "🌊", "desc": "Wave progression, evolution, and temporal structures."},
    "organism": {"category": "Organism", "icon": "🧬", "desc": "Living organism metrics and biological systems."},
    "mesh": {"category": "Mesh", "icon": "🕸️", "desc": "Topology, mesh networks, and node structures."},
    "hex": {"category": "Hex", "icon": "⬡", "desc": "Hex VM, grammars, and ritual execution."},
    "expansion": {"category": "Expansion", "icon": "🌿", "desc": "Mutation, seeds, and organic growth systems."},
    "dashboard": {"category": "Dashboard", "icon": "📊", "desc": "Visual interface and monitoring panels."},
    "paradox": {"category": "Paradox", "icon": "🔄", "desc": "Paradox resolution, temporal loops, identity splits."},
    "mycelial": {"category": "Mycelial", "icon": "🍄", "desc": "Mycelial networks, substrate intelligence, beliefs."},
    "temporal": {"category": "Temporal", "icon": "⏳", "desc": "Time mechanics, chrono-forge, temporal archives."},
    "void": {"category": "Void", "icon": "🌑", "desc": "Void mechanics, absence, negation structures."},
    "luminant": {"category": "Luminant", "icon": "✨", "desc": "Light, crystal, and luminous memory systems."},
}

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "catalog": {}, "entries": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def _detect_category(filename: str, title: str) -> dict:
    """Detect category from filename and title."""
    combined = (filename + " " + title).lower()
    for keyword, template in CATALOG_TEMPLATES.items():
        if keyword in combined:
            return template
    # Default based on wave number
    if "72" in filename or "71" in filename:
        return {"category": "Coherence", "icon": "🜂", "desc": "Recent organism evolution dashboard."}
    return {"category": "Dashboard", "icon": "📊", "desc": "IXPANSION monitoring panel."}

def build_catalog():
    """Scan all dashboards and build a catalog."""
    state = _load()
    entries = []
    
    if DASHBOARD_DIR.exists():
        for html_file in sorted(DASHBOARD_DIR.glob("*.html")):
            fname = html_file.name
            with open(html_file, 'r') as f:
                content = f.read()
            
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1).replace(' — IXPANSION', '') if title_match else fname
            
            category = _detect_category(fname, title)
            entry = {
                "id": hashlib.md5(fname.encode()).hexdigest()[:8],
                "filename": fname,
                "title": title,
                "wave": _extract_wave(fname),
                "category": category["category"],
                "icon": category["icon"],
                "desc": category["desc"],
                "status": "modernized" if "live" in content.lower() else "stale",
                "url": f"/dashboard/{fname}",
                "registered_at": datetime.datetime.now(datetime.UTC).isoformat()
            }
            entries.append(entry)
            state["catalog"][fname] = entry
    
    state["entries"] = entries
    state["total_entries"] = len(entries)
    state["categories"] = {}
    for e in entries:
        cat = e["category"]
        state["categories"].setdefault(cat, []).append(e["title"])
    
    _save(state)
    
    # Write the catalog JSON for public consumption
    catalog_data = {
        "name": "IXPANSION Dashboard Catalog",
        "wave": WAVE,
        "total": len(entries),
        "categories": state["categories"],
        "entries": entries
    }
    CATALOG_FILE.write_text(json.dumps(catalog_data, indent=2))
    
    return len(entries)

def _extract_wave(fname: str) -> str:
    import re
    match = re.search(r'(\d{3,4})', fname)
    return match.group(1) if match else "000"

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    
    if action == "build":
        count = build_catalog()
        return {"wave": WAVE, "action": "build", "catalog_entries": count}
    
    elif action == "entries":
        return {"wave": WAVE, "entries": state["entries"][-50:], "total": state.get("total_entries", 0)}
    
    elif action == "category":
        cat = req.get("category", "")
        cats = state.get("categories", {})
        return {"wave": WAVE, "category": cat, "entries": cats.get(cat, [])}
    
    elif action == "search":
        query = req.get("query", "").lower()
        results = [e for e in state["entries"] if query in e["title"].lower() or query in e.get("desc", "").lower()]
        return {"wave": WAVE, "query": query, "results": results}
    
    elif action == "status":
        return {"wave": WAVE, "name": NAME, "catalog_entries": state.get("total_entries", 0), "categories": len(state.get("categories", {})), "status": "active"}
    
    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "catalog_entries": state.get("total_entries", 0), "categories": len(state.get("categories", {})), "status": "active"}

def resonates_with() -> list:
    return [720, 721, 722, 728]

# Need re import

