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

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    import urllib.request
    token = os.environ.get("IXP_GITHUB_TOKEN", "")
    version = "4.68.0"
    wave = 515
    try:
        from api_server import VERSION, WAVE
        version = VERSION
        wave = int(WAVE)
    except Exception:
        pass
    # Check GitHub repo status
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
        "env": {
            "github_token": bool(os.environ.get("IXP_GITHUB_TOKEN")),
            "telegram_token": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        },
        "platform": "vercel",
        "live_url": "https://ixpansion-live.vercel.app",
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
