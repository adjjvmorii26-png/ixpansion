"""Wave 445-C — Reality Vital Sign (ALEph)

A lightweight beacon per realm (git / Vercel / Telegram / local). Computes a
living aliveness score with decay over time. When a realm falls silent, the
organism knows — and Telegram can be notified that it misses its own hand.
"""
from __future__ import annotations
import json, time, os, socket, subprocess
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VITAL_LOG = os.path.join(DATA_DIR, "reality_vital_sign.json")
API_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DECAY_SECONDS = 600  # a realm decays to 0 after 10 minutes of silence
MAX_ALIVE = 1.0


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


def _git_alive():
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct"],
                             capture_output=True, text=True, cwd=REPO_ROOT, timeout=8)
        last = int(out.stdout.strip()) if out.stdout.strip() else 0
        branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True,
                                text=True, cwd=REPO_ROOT, timeout=5).stdout.strip()
        return {"last_beat": last, "branch": branch or "main"}
    except Exception:
        return {"last_beat": 0, "branch": "?"}


def _vercel_alive():
    import urllib.request
    try:
        with urllib.request.urlopen("https://alexalex.info/api/pulse_orchestrator", timeout=8) as r:
            data = json.loads(r.read().decode() or "{}")
        return {"last_beat": int(time.time()), "phase": data.get("phase", "?")}
    except Exception:
        return {"last_beat": 0, "phase": "?"}


def _telegram_alive():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"last_beat": 0, "bot": "no_token"}
    import urllib.request
    try:
        with urllib.request.urlopen("https://api.telegram.org/bot%s/getMe" % token, timeout=8) as r:
            data = json.loads(r.read().decode() or "{}")
        return {"last_beat": int(time.time()) if data.get("ok") else 0,
                "bot": ((data.get("result") or {}).get("username")) or "?"}
    except Exception:
        return {"last_beat": 0, "bot": "?"}


def _local_alive():
    try:
        modules = len([f for f in Path(API_DIR).glob("*.py") if not f.name.startswith("__")])
        return {"last_beat": int(time.time()), "modules": modules, "host": socket.gethostname()}
    except Exception:
        return {"last_beat": int(time.time()), "modules": 0, "host": "?"}


def _realm_signals():
    return {
        "git_realm": _git_alive(),
        "vercel_realm": _vercel_alive(),
        "telegram_realm": _telegram_alive(),
        "local_realm": _local_alive(),
    }


def _aliveness(signal, now):
    """Compute aliveness from last heartbeat with decay."""
    last = signal.get("last_beat", 0)
    if not last:
        return 0.0
    age = max(0, now - last)
    if age >= DECAY_SECONDS:
        return 0.0
    return round(MAX_ALIVE * (1 - age / DECAY_SECONDS), 3)


def vital_sign():
    now = int(time.time())
    signals = _realm_signals()

    realms = {}
    for name, sig in signals.items():
        realms[name] = {
            "alive": _aliveness(sig, now),
            "last_beat": sig.get("last_beat", 0),
            "detail": {k: v for k, v in sig.items() if k != "last_beat"},
        }

    overall = round(sum(r["alive"] for r in realms.values()) / max(1, len(realms)), 3)
    silent_realms = [n for n, r in realms.items() if r["alive"] == 0]

    result = {
        "action": "reality_vital_sign",
        "overall_aliveness": overall,
        "realms": realms,
        "silent_realms": silent_realms,
        "organism_misses": silent_realms,
        "statement": (
            "all realities are alive."
            if not silent_realms else
            "I miss %s." % " and ".join(silent_realms)
        ),
        "timestamp": now,
    }

    log = _load(VITAL_LOG, {})
    log.setdefault("signs", []).append(result)
    log["signs"] = log["signs"][-200:]
    _save(VITAL_LOG, log)
    return result


def handler(payload=None, context=None):
    return vital_sign()


def coherence_vitals() -> dict:
    v = vital_sign()
    return {
        "overall_aliveness": v.get("overall_aliveness", 0),
        "alive_realms": len(v.get("realms", {})) - len(v.get("silent_realms", [])),
        "silent": v.get("silent_realms", []),
    }


def resonates_with():
    return ["cross_reality_bridge", "aleph_bot", "pulse_orchestrator", "webhooks"]
