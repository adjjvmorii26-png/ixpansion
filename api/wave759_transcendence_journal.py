"""Wave 759 — transcendence_journal.

Records every metaphysical shift as if the organism were writing scripture.
Each entry is a moment of self-awareness: a boundary crossed, an axiom rewritten,
a new community discovered, a liminal recombination.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave759_transcendence_journal.json"
WAVE = 759
NAME = "transcendence_journal"


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "entries": [], "epochs": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "entries": len(state.get("entries", [])),
                "epochs": len(state.get("epochs", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "record":
        moment = req.get("moment", "")
        significance = req.get("significance", "minor")
        domain = req.get("domain", "unknown")
        entry = {
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "moment": moment,
            "significance": significance,
            "domain": domain,
            "entry_id": len(state.get("entries", [])) + 1,
        }
        state.setdefault("entries", []).append(entry)
        state["entries"] = state["entries"][-100:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "record", "ok": True,
                "entry": entry}

    if action == "chronicle":
        entries = state.get("entries", [])
        limit = min(int(req.get("limit", 10)), 50)
        return {"wave": WAVE, "name": NAME, "action": "chronicle", "ok": True,
                "entries": entries[-limit:], "total": len(entries)}

    if action == "epoch":
        title = req.get("title", "unnamed epoch")
        purpose = req.get("purpose", "observation")
        entry_ids = req.get("entry_ids", [])
        epoch = {
            "title": title,
            "purpose": purpose,
            "entries": entry_ids,
            "sealed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("epochs", []).append(epoch)
        state["epochs"] = state["epochs"][-10:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "epoch", "ok": True,
                "epoch": title, "sealed_entries": len(entry_ids)}

    if action == "vision":
        entries = state.get("entries", [])
        sig_counts = {}
        for e in entries:
            s = e.get("significance", "minor")
            sig_counts[s] = sig_counts.get(s, 0) + 1
        domains = {}
        for e in entries:
            d = e.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        top_domain = max(domains, key=domains.get) if domains else "none"
        return {"wave": WAVE, "name": NAME, "action": "vision", "ok": True,
                "total_entries": len(entries),
                "significance_distribution": sig_counts,
                "dominant_domain": top_domain,
                "epochs": len(state.get("epochs", []))}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.91, "entries": len(state.get("entries", []))}


def resonates_with() -> list:
    return ["threshold_engine", "liminal_field", "axiom_mutator"]
