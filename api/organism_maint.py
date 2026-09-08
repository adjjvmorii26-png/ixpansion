"""Wave 515: Maintenance & Observability Suite — a group of small infrastructure modules.

Provides: env status, sync status, cron jobs, error log, webhooks, active modules,
release notes, backup status, and full health API.
"""
from __future__ import annotations
import json, os, time
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

REQUIRED_ENV = ["IXP_GITHUB_TOKEN"]
OPTIONAL_ENV = ["TELEGRAM_BOT_TOKEN"]


def _now() -> float:
    return time.time()


def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0, "entropy": 0.0}


def _env_status() -> Dict[str, Any]:
    """Report which environment variables are configured."""
    status = {}
    for var in REQUIRED_ENV + OPTIONAL_ENV:
        val = os.environ.get(var, "")
        status[var] = {
            "configured": bool(val),
            "prefix": val[:4] + "..." if val else "",
            "required": var in REQUIRED_ENV,
        }
    return {
        "action": "env_status",
        "configured": sum(1 for v in status.values() if v["configured"]),
        "total": len(status),
        "vars": status,
        "time": _now(),
    }


def _sync_status() -> Dict[str, Any]:
    """Track how long since last GitHub mirror writes."""
    topics = ["telegram_chat_ids", "execution_stack", "health_cache", "confluence_hub", "council_live"]
    now = _now()
    status = []
    for topic in topics:
        path = os.path.join(DATA_DIR, f"{topic}.json")
        mtime = os.path.getmtime(path) if os.path.exists(path) else 0
        age_min = round((now - mtime) / 60, 1) if mtime else None
        status.append({
            "topic": topic,
            "exists": os.path.exists(path),
            "last_modified_min": age_min,
            "fresh": age_min is not None and age_min < 60,
        })
    return {"action": "sync_status", "topics": status, "time": now}


def _cron_jobs() -> Dict[str, Any]:
    """List scheduled GitHub Actions workflows."""
    wf_dir = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows")
    jobs = []
    if os.path.isdir(wf_dir):
        for fname in sorted(os.listdir(wf_dir)):
            if fname.endswith(".yml"):
                path = os.path.join(wf_dir, fname)
                try:
                    with open(path) as f:
                        content = f.read()
                    import re
                    cron = re.search(r"cron:\s*'([^']+)'", content)
                    jobs.append({
                        "file": fname,
                        "cron": cron.group(1) if cron else None,
                        "name": os.path.splitext(fname)[0].replace("-", " ").title(),
                    })
                except Exception:
                    pass
    return {"action": "cron_jobs", "jobs": jobs, "count": len(jobs), "time": _now()}


def _error_log() -> Dict[str, Any]:
    """Aggregate error entries from data files."""
    errors = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json") and ("error" in fname or "fail" in fname):
            path = os.path.join(DATA_DIR, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    errors.extend(data[-20:])
                elif isinstance(data, dict) and "entries" in data:
                    errors.extend(data["entries"][-20:])
            except Exception:
                pass
    return {"action": "error_log", "entries": errors[-50:], "count": len(errors), "time": _now()}


def _webhooks() -> Dict[str, Any]:
    """List configured webhook endpoints."""
    hooks = [{"path": "/telegram-webhook", "target": "api.telegram_webhook", "status": "active"}]
    try:
        from api.aleph_bot import get_webhook_info
        info = get_webhook_info()
        hooks.append({"path": "/telegram-webhook", "target": "Telegram Bot API", "status": info.get("ok") and "connected" or "error"})
    except Exception:
        pass
    return {"action": "webhooks", "hooks": hooks, "count": len(hooks), "time": _now()}


def _active_modules() -> Dict[str, Any]:
    """Report platform active modules in this deployment."""
    try:
        from api.coherence_regulator import KNOWN_LIVING_MODULES
        total = len(KNOWN_LIVING_MODULES)
    except Exception:
        total = 0
    return {"action": "active_modules", "total": total, "category": "organism", "time": _now()}


def _release_notes() -> Dict[str, Any]:
    """Extract release notes from CHANGELOG."""
    path = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
    notes = []
    try:
        with open(path) as f:
            content = f.read()
        import re
        for m in re.finditer(r"## \[([\d.]+)\]\s*-\s*(.*?)\n\n(.*?)(?=\n## \[|\Z)", content, re.S):
            notes.append({"version": m.group(1), "title": m.group(2).strip(), "body": m.group(3).strip()[:500]})
    except Exception:
        pass
    return {"action": "release_notes", "releases": notes[:10], "count": len(notes), "time": _now()}


def _backup_status() -> Dict[str, Any]:
    """Report last backup times."""
    items = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(DATA_DIR, fname)
            mtime = os.path.getmtime(path)
            items.append({"file": fname, "last_modified": mtime, "age_min": round((_now() - mtime) / 60, 1)})
    return {"action": "backup_status", "files": items[:20], "count": len(items), "time": _now()}


def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "env_status")
    if action == "env_status": return _env_status()
    if action == "sync_status": return _sync_status()
    if action == "cron_jobs": return _cron_jobs()
    if action == "error_log": return _error_log()
    if action == "webhooks": return _webhooks()
    if action == "active_modules": return _active_modules()
    if action == "release_notes": return _release_notes()
    if action == "backup_status": return _backup_status()
    return {
        "module": "organism_maint",
        "wave": 515,
        "version": "4.68.0",
        "actions": ["env_status", "sync_status", "cron_jobs", "error_log", "webhooks",
                    "active_modules", "release_notes", "backup_status"],
        "vitals": coherence_vitals(),
    }
