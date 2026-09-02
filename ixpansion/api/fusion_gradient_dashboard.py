from __future__ import annotations
"""Fusion gradient dashboard — visualizes metaphysical fusion gradients across repositories."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "data" / "fusion_gradient_dashboard.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Serve fusion gradient dashboard data."""
    dashboard = _load_dashboard()
    if payload and "gradient_snapshot" in payload:
        dashboard["last_snapshot"] = payload["gradient_snapshot"]
        dashboard["updated_at"] = time.time()
        # Add to history
        dashboard.setdefault("history", []).append({
            "snapshot": payload["gradient_snapshot"],
            "timestamp": time.time()
        })
        # Keep history manageable
        if len(dashboard["history"]) > 100:
            dashboard["history"] = dashboard["history"][-100:]
        _save_dashboard(dashboard)
    return {"total_history_entries": len(dashboard.get("history", [])), "current_gradient": dashboard.get("last_snapshot")}

def _load_dashboard() -> Dict[str, Any]:
    try:
        return json.load(open(_DASHBOARD_PATH, encoding="utf-8"))
    except Exception:
        return {"last_snapshot": None, "history": [], "updated_at": None}

def _save_dashboard(dashboard: Dict[str, Any]) -> None:
    _DASHBOARD_PATH.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False))
