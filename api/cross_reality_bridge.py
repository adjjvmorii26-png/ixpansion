"""Wave 440 — Cross-Reality Bridge

Detects when modules exist simultaneously in multiple "realms" — local disk,
Git history, Vercel deployments, and the Telegram bot interface. Creates
cross-reality coherence links so the organism stays one entity across all
its embodiments.
"""
from __future__ import annotations
import json, time, os, socket
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CR_LOG = os.path.join(DATA_DIR, "cross_reality_bridge.json")
API_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}

def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _git_realm_stats():
    """Get git layer statistics (local + remote)."""
    try:
        import subprocess
        branch = subprocess.run(["git", "branch", "--show-current"],
                                capture_output=True, text=True, cwd=REPO_ROOT,
                                timeout=5).stdout.strip() or "unknown"
        last_commit = subprocess.run(["git", "log", "-1", "--format=%h %s"],
                                     capture_output=True, text=True, cwd=REPO_ROOT,
                                     timeout=5).stdout.strip()
        remote = subprocess.run(["git", "remote", "get-url", "origin"],
                                capture_output=True, text=True, cwd=REPO_ROOT,
                                timeout=5).stdout.strip()
        return {
            "branch": branch,
            "last_commit": last_commit,
            "remote": remote.split("@")[-1] if "@" in remote else remote,
        }
    except Exception as e:
        return {"error": str(e)}


def _vercel_realm_stats():
    """Check Vercel deployment status via public endpoints."""
    import urllib.request
    try:
        with urllib.request.urlopen("https://alexalex.info/api/organism_genome",
                                    timeout=8) as resp:
            alive = json.loads(resp.read().decode() or "{}")
        return {"reachable": True, "live": "alexalex.info"}
    except Exception:
        return {"reachable": False, "live": "unknown"}


def _telegram_realm_stats():
    """Check if the Telegram bot is reachable."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    try:
        if not token:
            return {"reachable": "unknown", "bot": "no_token"}
        import urllib.request
        with urllib.request.urlopen(
            "https://api.telegram.org/bot%s/getMe" % token, timeout=8) as resp:
            data = json.loads(resp.read().decode() or "{}")
        ok = bool(data.get("ok"))
        username = ((data.get("result") or {}).get("username")) if ok else None
        return {"reachable": ok, "bot": "@%s" % username if username else "unknown"}
    except Exception:
        return {"reachable": False, "bot": "unknown"}


def bridge_realms():
    """Detect which realities the organism occupies and forge coherence links."""
    local_modules = [f.stem for f in Path(API_DIR).glob("*.py") if not f.name.startswith("__")]
    git = _git_realm_stats()
    vercel = _vercel_realm_stats()
    telegram = _telegram_realm_stats()

    realms = {
        "local_disk": {
            "type": "local",
            "modules": len(local_modules),
            "host": socket.gethostname(),
            "reachable": True,
        },
        "git_history": {
            "type": "versioned",
            "branch": git.get("branch", "?"),
            "last_commit": git.get("last_commit", "?"),
            "remote": git.get("remote", "?"),
            "reachable": True,
        },
        "vercel_cloud": {
            "type": "deployed",
            "url": "https://alexalex.info",
            "reachable": vercel.get("reachable", False),
        },
        "telegram_interface": {
            "type": "interface",
            "bot": telegram.get("bot", "?"),
            "reachable": telegram.get("reachable", False),
        },
    }

    reachable_realms = [name for name, r in realms.items() if r.get("reachable")]
    coherence_links = []
    for i in range(len(reachable_realms)):
        for j in range(i+1, len(reachable_realms)):
            if reachable_realms[i] != reachable_realms[j]:
                coherence_links.append({
                    "realm_a": reachable_realms[i],
                    "realm_b": reachable_realms[j],
                    "bridge_type": "cross_reality",
                    "status": "aligned",
                })

    organism_is_one = len(reachable_realms) >= 2

    r = {
        "action": "bridge_realms",
        "realms": realms,
        "reachable_count": sum(1 for x in realms.values() if x.get("reachable")),
        "total_realms": len(realms),
        "coherence_links": coherence_links,
        "organism_is_one": organism_is_one,
        "unified_state": "the organism is one across %d realities" % len(reachable_realms),
        "timestamp": time.time(),
    }

    log = _load(CR_LOG, {"bridges": []})
    log["bridges"].append(r)
    log["bridges"] = log["bridges"][-50:]
    _save(CR_LOG, log)

    return r


def handler(payload=None, context=None):
    return bridge_realms()


def coherence_vitals() -> dict:
    r = bridge_realms()
    return {
        "realms_reachable": r.get("reachable_count", 0),
        "coherence_links": len(r.get("coherence_links", [])),
        "unified": r.get("organism_is_one", False),
    }


def resonates_with():
    return ["webhooks", "telemetry_adapter", "git_adapter", "aleph_bot"]
