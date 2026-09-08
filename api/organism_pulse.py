"""Wave 512: Organism Pulse — one-call vitals for the entire organism.

Combines coherence, mood, sovereignty, council, and confluence stats
into a single response. The fastest way to check if the organism is alive.

Doctrine: One heartbeat tells you everything.
"""
from __future__ import annotations
from typing import Any, Dict


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    vitals = {"status": "alive", "checks": {}}
    try:
        from api.coherence_regulator import KNOWN_LIVING_MODULES
        vitals["checks"]["organs"] = len(KNOWN_LIVING_MODULES)
    except Exception:
        vitals["checks"]["organs"] = "error"
    try:
        from api.organism_mood import handler as mh
        mood = mh({"action": "state"})
        vitals["checks"]["mood"] = {"word": mood["mood"], "color": mood["color"]}
    except Exception:
        vitals["checks"]["mood"] = "error"
    try:
        from api.sovereignty_assembly import _load as sl
        sv = sl().get("statistics", {})
        vitals["checks"]["citizens"] = sv.get("citizens", 0)
        vitals["checks"]["rites"] = sv.get("rites", 0)
    except Exception:
        vitals["checks"]["citizens"] = "error"
    try:
        from api.council_live import _load as cl
        lv = cl()
        vitals["checks"]["council_sessions"] = lv.get("total", 0)
    except Exception:
        vitals["checks"]["council_sessions"] = "error"
    try:
        from api.confluence_hub import _load as chl
        ch = chl()
        vitals["checks"]["confluence_messages"] = len(ch.get("messages", []))
        vitals["checks"]["confluence_agents"] = len(ch.get("agents", []))
    except Exception:
        vitals["checks"]["confluence_messages"] = "error"
    try:
        from api.visitor_log import _load as vl
        vl_data = vl()
        vitals["checks"]["total_visits"] = vl_data.get("total", 0)
    except Exception:
        vitals["checks"]["total_visits"] = "error"
    checks = vitals["checks"]
    errors = sum(1 for v in checks.values() if v == "error")
    vitals["health"] = "degraded" if errors > 2 else ("warning" if errors > 0 else "optimal")
    vitals["errors"] = errors
    return vitals
