#!/usr/bin/env python3
"""IX Kernel — enormous leap: self-extending lab runtime.

Beyond OS Boot. The kernel:
  1. Ignites Lab OS Boot
  2. Seals a constitutional epoch from organism DNA
  3. Emits silent caption package for @CoodingLooop
  4. Scaffolds the next free wave number (self-extension)
  5. Writes KERNEL_MANIFEST.json

  python lab/ops/ix_kernel.py --ignite
  python lab/ops/ix_kernel.py --ignite --scaffold --workers 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
API = ROOT / "api"
DATA = ROOT / "data"
CONTENT = ROOT / "content_output" / "kernel_captions"
MANIFEST = DATA / "ix_kernel_manifest.json"
CONSTITUTION = DATA / "ix_constitution.json"

sys.path.insert(0, str(OPS))
sys.path.insert(0, str(API))
sys.path.insert(0, str(ROOT))

WAVE_RE = re.compile(r"^wave(\d+)_")


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _soft(name: str, fn) -> Dict[str, Any]:
    t0 = time.perf_counter()
    try:
        out = fn()
        return {"phase": name, "ok": True, "ms": round((time.perf_counter() - t0) * 1000, 2), "result": out}
    except Exception as e:
        return {
            "phase": name,
            "ok": False,
            "ms": round((time.perf_counter() - t0) * 1000, 2),
            "error": f"{type(e).__name__}: {e}",
        }


def _next_wave_number() -> int:
    nums = []
    if API.is_dir():
        for p in API.glob("wave*.py"):
            m = WAVE_RE.match(p.stem)
            if m:
                nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 707


def _scaffold_wave(n: int, label: str = "kernel_spawn") -> Dict[str, Any]:
    safe = re.sub(r"[^a-z0-9_]", "_", label.lower())[:32]
    name = f"wave{n}_{safe}"
    path = API / f"{name}.py"
    if path.exists():
        return {"status": "exists", "path": str(path.relative_to(ROOT)), "wave": n}
    body = f'''"""Wave {n} {safe} — scaffolded by IX Kernel (self-extension).
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave{n}_{safe}.json"
DEFAULT = {{"module": "{name}", "wave": {n}, "spawned_by": "ix_kernel"}}


def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\\n")
        except OSError: pass


def coherence_vitals():
    st = _load()
    return {{"wave": {n}, "module": "{name}", "ok": True, "spawned_by": st.get("spawned_by")}}


def resonates_with():
    return ["wave706_lab_os_boot", "wave705_lab_jumpstart"]


def handler(req=None):
    req = req or {{}}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "awaken":
        st["awakened"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {{"status": "awakened", **coherence_vitals()}}
    if action == "status":
        return {{"status": "active", **st, **coherence_vitals()}}
    return {{"status": "unknown_action", "action": action, **coherence_vitals()}}


if __name__ == "__main__":
    print(json.dumps(handler({{"action": "status"}}), indent=2))
'''
    API.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return {"status": "scaffolded", "path": str(path.relative_to(ROOT)), "wave": n, "module": name}


def _silent_captions(fp: Optional[str], boot_ms: Any, layers_ok: Any) -> Dict[str, Any]:
    CONTENT.mkdir(parents=True, exist_ok=True)
    short = (fp or "void")[:16]
    frames = [
        {"t": 0, "text": "IX KERNEL IGNITE"},
        {"t": 2, "text": f"DNA {short}"},
        {"t": 4, "text": f"layers {layers_ok} · {boot_ms}ms"},
        {"t": 6, "text": "silence compounds"},
        {"t": 8, "text": "organism extends"},
        {"t": 10, "text": "@CoodingLooop"},
    ]
    package = {
        "channel": "@CoodingLooop",
        "style": "silent_caption_only",
        "palette": ["void", "cyan", "magenta"],
        "frames": frames,
        "fingerprint": fp,
        "ts": _utc(),
    }
    out = CONTENT / f"kernel_{short}_{int(time.time())}.json"
    out.write_text(json.dumps(package, indent=2) + "\n")
    return {"status": "emitted", "path": str(out.relative_to(ROOT)), "frames": len(frames)}


def _seal_constitution(fp: Optional[str], next_wave: int) -> Dict[str, Any]:
    epoch_id = hashlib.sha256(f"{fp}:{next_wave}:{_utc()}".encode()).hexdigest()[:16]
    rec = {
        "epoch_id": epoch_id,
        "fingerprint": fp,
        "next_wave": next_wave,
        "doctrine": [
            "lab_gates_neq_aleph_ci",
            "silence_is_product",
            "dna_delta_gates_work",
            "dirty_modules_isolate",
            "kernel_self_extends",
        ],
        "ts": _utc(),
    }
    history: List[Dict[str, Any]] = []
    if CONSTITUTION.exists():
        try:
            prev = json.loads(CONSTITUTION.read_text())
            history = list(prev.get("epochs") or [])[-31:]
        except Exception:
            pass
    history.append(rec)
    doc = {"status": "constitution", "epochs": history, "latest": rec}
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = CONSTITUTION.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, indent=2) + "\n")
        tmp.replace(CONSTITUTION)
    except OSError:
        pass
    return rec


def ignite(
    *,
    workers: int = 2,
    force: bool = False,
    scaffold: bool = False,
    seal_label: Optional[str] = None,
    captions: bool = True,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    phases: List[Dict[str, Any]] = []

    def _boot():
        from lab_os_boot import boot
        return boot(
            force=force,
            workers=workers,
            isolate_dirty=True,
            seal_label=seal_label or "ix_kernel",
            still_seconds=1.0,
        )

    boot_phase = _soft("os_boot", _boot)
    phases.append(boot_phase)

    fp = None
    layers_ok = None
    boot_ms = None
    if boot_phase.get("ok") and isinstance(boot_phase.get("result"), dict):
        r = boot_phase["result"]
        fp = r.get("fingerprint")
        layers_ok = r.get("layers_ok")
        boot_ms = r.get("ms")

    next_n = _next_wave_number()
    phases.append(_soft("constitution", lambda: _seal_constitution(fp, next_n)))

    if captions:
        phases.append(
            _soft("silent_captions", lambda: _silent_captions(fp, boot_ms, layers_ok))
        )

    scaffold_result = None
    if scaffold:
        sc = _soft("scaffold", lambda: _scaffold_wave(next_n, "kernel_spawn"))
        phases.append(sc)
        if sc.get("ok"):
            scaffold_result = sc.get("result")

    ok_n = sum(1 for p in phases if p.get("ok"))
    manifest = {
        "status": "ix_kernel",
        "ok": ok_n >= 2,
        "phases_ok": ok_n,
        "phases_total": len(phases),
        "ms": round((time.perf_counter() - t0) * 1000, 2),
        "fingerprint": fp,
        "next_wave": next_n,
        "scaffold": scaffold_result,
        "phases": phases,
        "ts": _utc(),
        "caption": "kernel · boot · constitution · silent frames · self-extend",
        "leap": "enormous",
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
    p = argparse.ArgumentParser(description="IX Kernel — self-extending lab runtime")
    p.add_argument("--ignite", action="store_true", default=True)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--force", action="store_true")
    p.add_argument("--scaffold", action="store_true")
    p.add_argument("--no-captions", action="store_true")
    p.add_argument("--seal", type=str, default=None)
    args = p.parse_args(argv)
    m = ignite(
        workers=args.workers,
        force=args.force,
        scaffold=args.scaffold,
        seal_label=args.seal,
        captions=not args.no_captions,
    )
    print(json.dumps(m, indent=2, default=str))
    return 0 if m.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
