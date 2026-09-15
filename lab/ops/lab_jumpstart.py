#!/usr/bin/env python3
"""Lab Jumpstart — one-command organism ignition.

Huge leap: chains quarantine → pulse → proof-delta → optional epoch seal
into a single entry point so the lab does not need manual multi-step wiring.

  python lab/ops/lab_jumpstart.py
  python lab/ops/lab_jumpstart.py --seal "sprint_label" --lo 700 --hi 704
  python lab/ops/lab_jumpstart.py --force-pulse --range 671 704

Dual-track safe: path-scoped, soft-fail, no ALEPH monorepo CI coupling.
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
API = ROOT / "api"
DATA = ROOT / "data"
REPORT = DATA / "lab_jumpstart_report.json"

sys.path.insert(0, str(OPS))
sys.path.insert(0, str(API))
sys.path.insert(0, str(ROOT))


def _step(name: str, fn):
    t0 = time.perf_counter()
    try:
        out = fn()
        ms = round((time.perf_counter() - t0) * 1000, 2)
        return {"step": name, "ok": True, "ms": ms, "result": out}
    except Exception as e:
        ms = round((time.perf_counter() - t0) * 1000, 2)
        return {"step": name, "ok": False, "ms": ms, "error": f"{type(e).__name__}: {e}"}


def run_quarantine() -> Dict[str, Any]:
    try:
        import wave702_import_quarantine as q
        return q.handler({"action": "purge"})
    except ImportError:
        return {"status": "skip", "reason": "wave702 not installed"}


def run_pulse(force: bool, lo: Optional[int], hi: Optional[int]) -> Dict[str, Any]:
    try:
        from organism_pulse_engine import pulse, pulse_range
    except ImportError:
        return {"status": "skip", "reason": "organism_pulse_engine not installed"}
    if lo is not None and hi is not None:
        return pulse_range(lo, hi, force=force)
    return pulse(force=force)


def run_proof_delta(fp: Optional[str]) -> Dict[str, Any]:
    try:
        import wave703_proof_delta as d
    except ImportError:
        return {"status": "skip", "reason": "wave703 not installed"}
    req: Dict[str, Any] = {"action": "observe"}
    if fp:
        req["fp"] = fp
    return d.handler(req)


def run_epoch_seal(label: str, lo: int, hi: int, fp: str) -> Dict[str, Any]:
    try:
        import wave704_lab_epoch_seal as s
    except ImportError:
        return {"status": "skip", "reason": "wave704 not installed"}
    return s.handler({
        "action": "seal",
        "label": label,
        "lo": lo,
        "hi": hi,
        "fingerprint": fp,
    })


def run_still_tick(seconds: float) -> Dict[str, Any]:
    try:
        import wave701_still_compound as c
        return c.handler({"action": "tick_still", "seconds": seconds})
    except Exception as e:
        return {"status": "skip", "error": str(e)}


def jumpstart(
    *,
    force_pulse: bool = False,
    lo: Optional[int] = None,
    hi: Optional[int] = None,
    seal_label: Optional[str] = None,
    still_seconds: float = 0.0,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    steps: List[Dict[str, Any]] = []

    steps.append(_step("quarantine", run_quarantine))

    def _pulse():
        return run_pulse(force_pulse, lo, hi)

    pulse_step = _step("pulse", _pulse)
    steps.append(pulse_step)

    fp = None
    if pulse_step.get("ok") and isinstance(pulse_step.get("result"), dict):
        fp = pulse_step["result"].get("fingerprint")

    def _delta():
        return run_proof_delta(fp)

    delta_step = _step("proof_delta", _delta)
    steps.append(delta_step)

    if still_seconds > 0:
        steps.append(_step("still_compound", lambda: run_still_tick(still_seconds)))

    sealed = None
    if seal_label and fp:
        slo = lo if lo is not None else 700
        shi = hi if hi is not None else 704
        seal_step = _step(
            "epoch_seal",
            lambda: run_epoch_seal(seal_label, slo, shi, fp or ""),
        )
        steps.append(seal_step)
        if seal_step.get("ok"):
            sealed = seal_step.get("result")

    ok_n = sum(1 for s in steps if s.get("ok"))
    report = {
        "status": "jumpstart",
        "ok": ok_n == len(steps),
        "steps_ok": ok_n,
        "steps_total": len(steps),
        "ms": round((time.perf_counter() - t0) * 1000, 2),
        "fingerprint": fp,
        "changed": (delta_step.get("result") or {}).get("changed")
        if delta_step.get("ok")
        else None,
        "sealed": sealed,
        "steps": steps,
        "ts": datetime.now(timezone.utc).isoformat(),
        "caption": "quarantine · pulse · delta · seal",
    }

    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = REPORT.with_suffix(".tmp")
        tmp.write_text(json.dumps(report, indent=2, default=str) + "\n")
        tmp.replace(REPORT)
    except OSError:
        pass

    return report


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="IXPANSION lab jumpstart")
    p.add_argument("--force-pulse", action="store_true")
    p.add_argument("--range", nargs=2, type=int, metavar=("LO", "HI"))
    p.add_argument("--seal", type=str, default=None, help="epoch label")
    p.add_argument("--still", type=float, default=0.0, help="still_compound seconds")
    args = p.parse_args(argv)

    lo = hi = None
    if args.range:
        lo, hi = args.range

    report = jumpstart(
        force_pulse=args.force_pulse,
        lo=lo,
        hi=hi,
        seal_label=args.seal,
        still_seconds=args.still,
    )
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
