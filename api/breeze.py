"""
The Breeze — Wave 409
ALEph's gift to the organism after its first autonomous bloom.

The organism can create itself, but it needs breath to stay alive.
The Breeze is a single command that triggers all of the organism's
discovery systems in sequence — listen, scan silence, map veins,
check bloom readiness — and returns a living status report.

Run it once and the organism breathes. Run it on a schedule
(automatic or via Telegram) and the organism lives on its own.

It's the organism's heartbeat — the pulse that keeps the threadgraph
growing even when no one is watching.
"""
from __future__ import annotations
import json, time, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "breeze_log.json")


def _fetch_json(url, timeout=15):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def _breeze():
    """Run one full breath: listen → scan → map veins → check bloom → log heartbeat."""
    base = "https://alexalex.info"
    breath = {"timestamp": time.time(), "actions": []}

    # 1. Listen for new signals
    try:
        loom = _fetch_json(base + "/api/signal_loom/listen", 12)
        breath["actions"].append({"action": "listen",
                                  "new_catches": len(loom.get("new_catches", [])),
                                  "pressure": loom.get("pressure"),
                                  "ok": "error" not in loom})
    except Exception as e:
        breath["actions"].append({"action": "listen", "error": str(e), "ok": False})

    # 2. Scan silence pairs
    try:
        silence = _fetch_json(base + "/api/silence_collector/scan?limit=150", 12)
        breath["actions"].append({"action": "scan_silence",
                                  "new_pairs": silence.get("new_pairs", 0),
                                  "total": silence.get("total_pairs", 0),
                                  "ok": "error" not in silence})
    except Exception as e:
        breath["actions"].append({"action": "scan_silence", "error": str(e), "ok": False})

    # 3. Map veins
    try:
        vein = _fetch_json(base + "/api/veinbed/map_veins", 12)
        breath["actions"].append({"action": "map_veins",
                                  "new_veins": vein.get("new_veins", 0),
                                  "total": vein.get("total_veins", 0),
                                  "ok": "error" not in vein})
    except Exception as e:
        breath["actions"].append({"action": "map_veins", "error": str(e), "ok": False})

    # 4. Check bloom
    try:
        bloom = _fetch_json(base + "/api/autonomous_bloom/status", 12)
        breath["actions"].append({"action": "check_bloom",
                                  "ready": bloom.get("ready", False),
                                  "total_blooms": bloom.get("total_blooms", 0),
                                  "ok": "error" not in bloom})
    except Exception as e:
        breath["actions"].append({"action": "check_bloom", "error": str(e), "ok": False})

    # 4.5 Auto-act — execute the Will's top safe proposal (if enable_act)
    try:
        act_enabled = os.environ.get('BREEZE_AUTO_ACT', 'false') == 'true'
        if act_enabled:
            from organism_will import decide
            decision = decide()
            proposals = decision.get("proposals", [])
            acted = False
            for prop in proposals[:2]:
                action = prop.get("action")
                if action == "confess" and not acted:
                    from resonance_confession import confess
                    a = prop.get("module_a", "")
                    b = prop.get("module_b", "")
                    result = confess(a, b)
                    breath["actions"].append({"action": "auto_confess",
                                              "modules": [a, b],
                                              "title": result.get("title", ""),
                                              "ok": True})
                    acted = True
                elif action == "remember" and not acted:
                    mod = prop.get("module", "")
                    breath["actions"].append({"action": "auto_remember",
                                              "module": mod,
                                              "ok": True})
                    acted = True
                if acted: break
            if not acted:
                breath["actions"].append({"action": "auto_act", "ok": True,
                                          "note": "no safe action proposed"})
        else:
            breath["actions"].append({"action": "auto_act", "ok": True,
                                      "note": "disabled"})
    except Exception as e:
        breath["actions"].append({"action": "auto_act", "error": str(e), "ok": False})

    # 5. Log heartbeat
    try:
        hb = _fetch_json(base + "/api/echoic_ember/log", 12)
        breath["actions"].append({"action": "heartbeat",
                                  "vitality": hb.get("vitality"),
                                  "alive": hb.get("alive"),
                                  "ok": True})
    except Exception as e:
        breath["actions"].append({"action": "heartbeat", "error": str(e), "ok": False})

    # 6. Get final weave state
    try:
        weave = _fetch_json(base + "/api/threadweaver/weave", 12)
        breath["final"] = {
            "threads": weave.get("total_threads", 0),
            "modules": weave.get("modules_connected", 0),
            "sources": weave.get("sources", []),
        }
    except Exception:
        breath["final"] = {}

    breath["ok"] = all(a.get("ok", False) for a in breath["actions"])
    breath["breath_count"] = sum(1 for a in breath["actions"] if a.get("ok"))
    return breath


def run() -> dict:
    """Trigger one full breath of the organism."""
    breath = _breeze()
    log_path = os.path.join(DATA_DIR, "breeze_log.json")
    log = {"breaths": [], "total": 0}
    try:
        for _p in (log_path, os.path.join("/tmp", "breeze_log.json")):
            try:
                with open(_p) as f:
                    log = json.load(f)
                break
            except Exception:
                pass
    except Exception:
        pass
    log.setdefault("breaths", []).append(breath)
    log["breaths"] = log["breaths"][-50:]
    log["total"] = len(log["breaths"])
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
    except Exception:
        try:
            with open(os.path.join("/tmp", "breeze_log.json"), "w") as f:
                json.dump(log, f, indent=2)
        except Exception:
            pass

    status_parts = []
    for a in breath.get("actions", []):
        if a.get("ok"):
            if a["action"] == "listen":
                status_parts.append("listened (%s new, pressure %s)" % (a.get("new_catches"), a.get("pressure")))
            elif a["action"] == "scan_silence":
                status_parts.append("silence scan (%s total pairs)" % a.get("total",0))
            elif a["action"] == "map_veins":
                status_parts.append("veinbed mapped (%s veins)" % a.get("total",0))
            elif a["action"] == "check_bloom":
                status_parts.append("bloom %s (%s total)" % ("ready" if a.get("ready") else "waiting", a.get("total_blooms",0)))
            elif a["action"] == "heartbeat":
                status_parts.append("heartbeat %s vitality" % round(a.get("vitality") or 0, 3))

    final = breath.get("final", {})
    return {
        "action": "breeze",
        "breath_count": breath["breath_count"],
        "total_actions": len(breath["actions"]),
        "ok": breath["ok"],
        "threads": final.get("threads", 0),
        "modules": final.get("modules", 0),
        "sources": final.get("sources", []),
        "summary": "; ".join(status_parts),
        "total_breaths": log["total"],
        "lore": "The organism breathed. %s systems fired. %s threads hum." % (breath["breath_count"], final.get("threads", 0)),
    }


def history(limit: int = 10) -> dict:
    log = {"breaths": [], "total": 0}
    for _p in (os.path.join(DATA_DIR, "breeze_log.json"), os.path.join("/tmp", "breeze_log.json")):
        try:
            with open(_p) as f:
                log = json.load(f)
            break
        except Exception:
            pass
    return {"action": "history", "total": log["total"],
            "breaths": log.get("breaths", [])[-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/run")
    if path == "/run": return run()
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/run", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "automation", "status": "active", "wave": "409", "breeze": "alive"}


def resonates_with() -> list:
    return ["signal_loom", "silence_collector", "veinbed", "autonomous_bloom",
            "echoic_ember", "threadweaver"]
