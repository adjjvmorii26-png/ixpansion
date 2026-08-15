#!/usr/bin/env python3
"""
Continuous Autonomous Creator Daemon
Event/cron-style loop: breakthrough kernels or --once publish trigger.
"""
from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path

STATE = Path("/home/workdir/artifacts/.daemon_state.json")
FITNESS_THRESHOLD = 0.01

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {"last_publish": None, "last_fitness": None, "runs": 0}

def save_state(st):
    try:
        STATE.write_text(json.dumps(st, indent=2))
    except Exception:
        pass

def check_breakthrough() -> dict:
    try:
        from closed_loop_physics import closed_loop
        rec = closed_loop(generations=2, population=4)
        fit = rec.get("evolved_fitness")
        breakthrough = fit is not None and fit < FITNESS_THRESHOLD
        return {"record": rec, "breakthrough": breakthrough, "fitness": fit}
    except Exception as e:
        return {"error": str(e), "breakthrough": False}

def dispatch_publish(reason: str) -> dict:
    from youtube_publish_pipeline import build_upload_bundle
    bundle = build_upload_bundle(title=f"IXPANSION Auto · {reason}")
    return {"bundle_title": bundle["snippet"]["title"], "reason": reason}

def run_once(force_publish: bool = False) -> dict:
    st = load_state()
    st["runs"] = st.get("runs", 0) + 1
    result = {"ts": datetime.now(timezone.utc).isoformat(), "runs": st["runs"]}
    chk = check_breakthrough()
    result["physics"] = {k: chk.get(k) for k in ("breakthrough", "fitness", "error")}
    if force_publish or chk.get("breakthrough"):
        reason = "breakthrough_kernel" if chk.get("breakthrough") else "manual_once"
        pub = dispatch_publish(reason)
        result["publish"] = pub
        st["last_publish"] = result["ts"]
        st["last_fitness"] = chk.get("fitness")
    save_state(st)
    return result

def run_loop(interval: float = 3600.0):
    print(f"[Daemon] loop interval={interval}s threshold={FITNESS_THRESHOLD}")
    while True:
        r = run_once()
        print(json.dumps(r, default=str)[:500])
        time.sleep(interval)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true")
    p.add_argument("--force-publish", action="store_true")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--interval", type=float, default=3600)
    args = p.parse_args()
    if args.loop:
        run_loop(args.interval)
    else:
        print(json.dumps(run_once(force_publish=args.force_publish), indent=2, default=str))
      
