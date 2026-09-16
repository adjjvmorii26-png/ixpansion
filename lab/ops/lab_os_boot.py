#!/usr/bin/env python3
"""Lab OS Boot — bigger than jumpstart: full lab operating-system ignition.

Layers:
  1. Jumpstart (quarantine → pulse → proof_delta → optional seal)
  2. Parallel / isolated pulse upgrade (workers + subprocess dirty modules)
  3. Dual-track posture card (soft)
  4. Velocity family tick (soft)
  5. BOOT_MANIFEST.json — single artifact for CI / dashboards / agents

  python lab/ops/lab_os_boot.py
  python lab/ops/lab_os_boot.py --workers 4 --force --seal "os_boot"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
DATA = ROOT / "data"
MANIFEST = DATA / "lab_os_boot_manifest.json"

sys.path.insert(0, str(OPS))
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))


def _soft(name: str, fn) -> Dict[str, Any]:
    t0 = time.perf_counter()
    try:
        out = fn()
        return {"layer": name, "ok": True, "ms": round((time.perf_counter() - t0) * 1000, 2), "result": out}
    except Exception as e:
        return {
            "layer": name,
            "ok": False,
            "ms": round((time.perf_counter() - t0) * 1000, 2),
            "error": f"{type(e).__name__}: {e}",
        }


def boot(
    *,
    force: bool = False,
    workers: int = 2,
    isolate_dirty: bool = True,
    seal_label: Optional[str] = None,
    still_seconds: float = 1.0,
    lo: Optional[int] = None,
    hi: Optional[int] = None,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    layers: List[Dict[str, Any]] = []

    def _js():
        from lab_jumpstart import jumpstart
        return jumpstart(
            force_pulse=force,
            lo=lo,
            hi=hi,
            seal_label=seal_label,
            still_seconds=still_seconds,
        )

    js = _soft("jumpstart", _js)
    layers.append(js)

    def _pulse2():
        from organism_pulse_engine import pulse, pulse_range
        if lo is not None and hi is not None:
            return pulse_range(lo, hi, force=force, workers=workers, isolate_dirty=isolate_dirty)
        return pulse(force=force, workers=workers, isolate_dirty=isolate_dirty)

    def _pulse2_safe():
        try:
            return _pulse2()
        except TypeError:
            from organism_pulse_engine import pulse, pulse_range
            if lo is not None and hi is not None:
                return pulse_range(lo, hi, force=force)
            return pulse(force=force)

    layers.append(_soft("pulse_parallel", _pulse2_safe))

    def _dual():
        try:
            import dual_track_card as d
            if hasattr(d, "handler"):
                return d.handler({"action": "status"})
            if hasattr(d, "main"):
                return {"status": "present"}
            return {"status": "module_ok"}
        except ImportError:
            return {"status": "skip", "reason": "dual_track_card missing"}

    layers.append(_soft("dual_track", _dual))

    def _vel():
        try:
            import wave690_momentum_braid as m
            return m.handler({"action": "tick", "lab_v": 2.0, "aleph_v": 1.8})
        except ImportError:
            return {"status": "skip"}

    layers.append(_soft("momentum", _vel))

    fp = None
    if js.get("ok") and isinstance(js.get("result"), dict):
        fp = js["result"].get("fingerprint")
    for L in layers:
        if L.get("layer") == "pulse_parallel" and L.get("ok"):
            r = L.get("result") or {}
            fp = r.get("fingerprint") or fp

    ok_n = sum(1 for L in layers if L.get("ok"))
    manifest = {
        "status": "lab_os_boot",
        "ok": ok_n >= 1,
        "layers_ok": ok_n,
        "layers_total": len(layers),
        "ms": round((time.perf_counter() - t0) * 1000, 2),
        "fingerprint": fp,
        "workers": workers,
        "isolate_dirty": isolate_dirty,
        "layers": layers,
        "ts": datetime.now(timezone.utc).isoformat(),
        "caption": "os boot · jumpstart · parallel pulse · isolate · dual-track",
        "recommendations": [
            "Merge PRs #122 #123 #124 before relying on full seal/still stack on main",
            "Wire lab-os-boot.yml as path-filtered CI gate",
            "Add conftest quarantine after data reset",
            "Dashboard strip for BOOT_MANIFEST fingerprint",
        ],
    }

    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = MANIFEST.with_suffix(".tmp")
        tmp.write_text(json.dumps(manifest, indent=2, default=str) + "\n")
        tmp.replace(MANIFEST)
    except OSError:
        pass

    return manifest


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="IXPANSION Lab OS Boot")
    p.add_argument("--force", action="store_true")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--no-isolate", action="store_true")
    p.add_argument("--seal", type=str, default=None)
    p.add_argument("--still", type=float, default=1.0)
    p.add_argument("--range", nargs=2, type=int, metavar=("LO", "HI"))
    args = p.parse_args(argv)
    lo = hi = None
    if args.range:
        lo, hi = args.range
    m = boot(
        force=args.force,
        workers=args.workers,
        isolate_dirty=not args.no_isolate,
        seal_label=args.seal,
        still_seconds=args.still,
        lo=lo,
        hi=hi,
    )
    print(json.dumps(m, indent=2, default=str))
    return 0 if m.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
