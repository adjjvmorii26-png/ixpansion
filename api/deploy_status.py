"""Wave 516: Deployment Status — tracks deploy history and environment health."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}
def resonates_with():
    return ['organism_core', 'coherence_validator', 'consensus_bloom', 'council_oracle', 'causality_weave']


def deployment_reality_check() -> dict:
    """Report non-secret runtime capability mismatches.

    Probes the auth store when available — status is not based on env names alone.
    Never reports credential values or secret-presence booleans.
    """
    serverless = bool(os.environ.get("VERCEL") or os.environ.get("NOW_REGION"))
    persistence = os.environ.get("IXPANSION_AUTH_STORE", "").strip().lower()
    store_ok = False
    store_name = "none"
    try:
        from api import auth_store as auth_store_mod
        from api.auth_store import get_auth_store
        active = auth_store_mod._ACTIVE_STORE
        if active is not None:
            h = active.health()
            store_ok = bool(h.get("ok"))
            store_name = str(h.get("name") or active.name)
        elif not serverless:
            h = get_auth_store().health()
            store_ok = bool(h.get("ok"))
            store_name = str(h.get("name") or "local_json")
    except Exception as e:
        store_ok = False
        store_name = f"error:{type(e).__name__}"
    durable = store_ok and store_name not in {"local_json", "none", "abstract"}
    if not serverless:
        status = "ready" if store_ok else "degraded"
    else:
        status = "ready" if durable else "blocked"
    return {
        "serverless": serverless,
        "auth_persistence": "durable" if durable else "local_or_unconfigured",
        "store": store_name,
        "store_operational": store_ok,
        "named_backend": persistence or None,
        "status": status,
    }


def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    import urllib.request
    version = "4.68.0"
    wave = 515
    try:
        from api_server import VERSION, WAVE
        version = VERSION
        wave = int(WAVE)
    except Exception:
        pass
    repo_ok = False
    last_commit = ""
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/adjjvmorii26-png/ixpansion/commits?per_page=1",
            headers={"User-Agent": "ixpansion-deploy", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data and isinstance(data, list):
                last_commit = data[0].get("sha", "")[:8]
                repo_ok = True
    except Exception:
        pass
    return {
        "action": "deploy_status",
        "version": version,
        "wave": wave,
        "github": {"connected": repo_ok, "last_commit": last_commit},
        "platform": "vercel",
        "time": time.time(),
        "vitals": coherence_vitals(),
        "reality": deployment_reality_check(),
    }
