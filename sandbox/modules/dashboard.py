#!/usr/bin/env python3
"""Aggregate last module outputs into a dashboard snapshot."""
from __future__ import annotations
import json, time
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output"

def run(*_):
    cards = []
    for p in sorted(OUT.glob("*_last.json")):
        try:
            data = json.loads(p.read_text())
            cards.append({"file": p.name, "module": data.get("module", p.stem), "summary": _summarize(data)})
        except Exception as e:
            cards.append({"file": p.name, "error": e.__class__.__name__})
    dash = {"module": "dashboard", "title": "IXPANSION Sandbox Dashboard", "cards": cards, "ts": time.time()}
    path = OUT / "dashboard.html"
    path.write_text(_html(dash))
    dash["html"] = str(path)
    return dash

def _summarize(d: dict) -> str:
    if "lineage" in d: return d["lineage"][-1][:80]
    if "biomes" in d: return f"{len(d['biomes'])} biomes, {len(d.get('portals', []))} portals"
    if "actions" in d: return d["actions"][0][:80]
    if "agents" in d: return ", ".join(a["id"] for a in d["agents"])
    if "messages" in d: return f"{len(d['messages'])} messages"
    return "ok"

def _html(dash: dict) -> str:
    rows = "".join(f"<tr><td>{c.get('module','')}</td><td>{c.get('summary', c.get('error',''))}</td></tr>" for c in dash["cards"])
    return f"""<!DOCTYPE html><html><head><meta charset=\"utf-8\"/><title>Sandbox Dashboard</title>
<style>body{{background:#07070c;color:#c8d0e0;font-family:ui-monospace,monospace;padding:2rem;}}
h1{{color:#7cffa0;}}table{{border-collapse:collapse;width:100%;max-width:900px;}}
td,th{{border:1px solid #1a1a28;padding:.5rem;text-align:left;}}</style></head><body>
<h1>SANDBOX</h1><table><tr><th>Module</th><th>Summary</th></tr>{rows}</table></body></html>"""
