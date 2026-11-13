"""Autonomous, read-only storage supervision for IXPANSION.

The guardian observes storage health and emits bounded remediation guidance.
It never changes credentials, deletes durable records, changes provider config,
or promotes an ephemeral backend to authoritative status.
"""
from __future__ import annotations
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List
from api import off_vercel_store


def _cache_probe() -> Dict[str, Any]:
    path = os.environ.get("IXP_SQUIRREL_CACHE_PATH", "/tmp/ixp_squirrel_cache.sqlite3")
    result: Dict[str, Any] = {
        "path": path, "present": False, "integrity": "not_checked",
        "entries": None, "bytes": None, "durable": False, "authority": False,
    }
    if not Path(path).exists():
        return result
    result["present"] = True
    try:
        uri = Path(path).resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=2) as db:
            check = db.execute("PRAGMA quick_check").fetchone()
            result["integrity"] = check[0] if check else "unknown"
            if result["integrity"] == "ok":
                row = db.execute(
                    "SELECT COUNT(*), COALESCE(SUM(byte_size), 0) FROM cache_entries"
                ).fetchone()
                result["entries"], result["bytes"] = row
    except sqlite3.Error as exc:
        result["integrity"] = "unavailable"
        result["error_type"] = type(exc).__name__
    return result


def inspect_storage() -> Dict[str, Any]:
    """Return a secret-free storage health report and safe next actions."""
    recommendations: List[str] = []
    try:
        selected = off_vercel_store.backend()
        config_ok = True
    except off_vercel_store.StoreConfigurationError:
        selected, config_ok = "misconfigured", False
    durable = selected in {"upstash", "http"}
    if not config_ok:
        status = "BLOCKED"
        recommendations.append("Repair paired durable-backend configuration; do not fall back to /tmp.")
    elif not durable:
        status = "DEGRADED"
        recommendations.append("Provision and verify an external durable backend before persisting critical state.")
        if selected == "github_cold":
            recommendations.append("Keep GitHub in cold-archive role; it is not an atomic hot-path database.")
        else:
            recommendations.append("Treat /tmp as disposable and refuse critical writes without a durable backend.")
    else:
        status = "HEALTHY_CONFIGURED"
        recommendations.append("Run an authenticated read/write/read-back probe before claiming backend availability.")
    cache = _cache_probe()
    if cache["integrity"] not in {"ok", "not_checked"}:
        if status == "HEALTHY_CONFIGURED":
            status = "DEGRADED"
        recommendations.append("Quarantine the ephemeral cache instance and rebuild it; never delete durable records.")
    return {
        "component": "storage_guardian", "status": status, "backend": selected,
        "backend_configured": config_ok, "durable_backend_configured": durable,
        "backend_reachability": "NOT_PROBED", "cache": cache,
        "recommendations": recommendations,
        "autonomy": {
            "mode": "observe_and_safe_ephemeral_maintenance", "may_change_credentials": False,
            "may_delete_durable_data": False, "may_change_provider_configuration": False,
            "may_claim_unverified_durability": False,
        },
    }



def maintain_ephemeral_cache(now: float | None = None) -> Dict[str, Any]:
    """Safely remove expired rows from the disposable local cache only.

    This is the guardian's first autonomous repair: bounded by cache TTL and
    isolated to the configured SquirrelCache SQLite file. It never touches the
    authoritative remote backend or any application data files.
    """
    path = os.environ.get("IXP_SQUIRREL_CACHE_PATH", "/tmp/ixp_squirrel_cache.sqlite3")
    if not Path(path).is_file():
        return {"action": "skipped", "reason": "cache_absent", "expired_removed": 0}
    try:
        uri = Path(path).resolve().as_uri() + "?mode=rw"
        with sqlite3.connect(uri, uri=True, timeout=3) as db:
            db.execute("PRAGMA busy_timeout=3000")
            integrity = db.execute("PRAGMA quick_check").fetchone()
            if not integrity or integrity[0] != "ok":
                return {"action": "blocked", "reason": "cache_integrity_failed",
                        "expired_removed": 0}
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                "DELETE FROM cache_entries WHERE expires_at <= ?",
                (float(time.time() if now is None else now),),
            )
            removed = cursor.rowcount
            db.execute("COMMIT")
            verified = db.execute("PRAGMA quick_check").fetchone()
            if not verified or verified[0] != "ok":
                return {"action": "degraded", "reason": "post_maintenance_check_failed",
                        "expired_removed": removed}
        return {"action": "completed", "reason": "expired_cache_entries_pruned",
                "expired_removed": removed, "durable_data_touched": False}
    except sqlite3.Error as exc:
        return {"action": "failed", "reason": type(exc).__name__,
                "expired_removed": 0, "durable_data_touched": False}

def coherence_vitals() -> Dict[str, Any]:
    report = inspect_storage()
    return {
        "module": "storage_guardian", "ok": report["status"] == "HEALTHY_CONFIGURED",
        "status": report["status"],
        "durable_backend_configured": report["durable_backend_configured"],
        "backend_reachability": report["backend_reachability"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(inspect_storage(), indent=2, sort_keys=True))
