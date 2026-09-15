#!/usr/bin/env python3
"""OUROBOROS — infinite leap: the organism that eats its own DNA and dreams the next organ.

Unique idea: fingerprint bits are not just integrity — they are a *dream seed*.
Each recurrence:
  1. Reads organism DNA (or ignites kernel to obtain it)
  2. Decodes a mythic organ name from the hex (dream lexicon)
  3. Scaffolds that organ as a void-twin
  4. Appends an eternal recurrence ledger (never overwrite — only grow)
  5. Optionally re-enters (max_cycles safety for CI)

  python lab/ops/ouroboros.py --once
  python lab/ops/ouroboros.py --cycles 3 --scaffold
  python lab/ops/ouroboros.py --dream-only
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
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
API = ROOT / "api"
DATA = ROOT / "data"
LEDGER = DATA / "ouroboros_ledger.jsonl"
MANIFEST = DATA / "ouroboros_manifest.json"
DREAMS = DATA / "ouroboros_dreams.json"

sys.path.insert(0, str(OPS))
sys.path.insert(0, str(API))
sys.path.insert(0, str(ROOT))

LEX_A = (
    "void", "echo", "scar", "hush", "tide", "braid", "ember", "glyph",
    "rift", "loom", "still", "bloom", "crown", "ghost", "pulse", "dawn",
)
LEX_B = (
    "mirror", "lattice", "choir", "garden", "membrane", "orbit", "quill",
    "archive", "horizon", "residue", "cascade", "nexus", "veil", "spark",
    "well", "forge",
)
LEX_C = (
    "dream", "twin", "fold", "ash", "root", "wing", "knot", "seed",
    "trace", "flux", "halo", "shard", "reed", "mist", "coil", "span",
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def dream_name(fingerprint: str) -> Tuple[str, Dict[str, Any]]:
    fp = re.sub(r"[^0-9a-fA-F]", "", fingerprint or "") or "0" * 16
    if len(fp) < 6:
        fp = (fp + "0" * 6)[:6]
    b0 = int(fp[0:2], 16)
    b1 = int(fp[2:4], 16)
    b2 = int(fp[4:6], 16)
    a = LEX_A[b0 % len(LEX_A)]
    b = LEX_B[b1 % len(LEX_B)]
    c = LEX_C[b2 % len(LEX_C)]
    salt = fp[6:10] if len(fp) >= 10 else fp[:4]
    name = f"{a}_{b}_{c}"
    slug = f"{a}_{b}_{c}_{salt.lower()}"
    meta = {
        "name": name,
        "slug": slug,
        "parts": [a, b, c],
        "salt": salt.lower(),
        "seed_bytes": [b0, b1, b2],
    }
    return slug, meta


def _next_wave() -> int:
    nums = []
    if API.is_dir():
        for p in API.glob("wave*.py"):
            m = re.match(r"wave(\d+)_", p.stem)
            if m:
                nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 708


def _obtain_fingerprint(force: bool = False) -> Optional[str]:
    for path in (
        DATA / "organism_fingerprint.hex",
        DATA / "ix_kernel_manifest.json",
        DATA / "lab_os_boot_manifest.json",
    ):
        if not path.exists():
            continue
        try:
            if path.suffix == ".hex":
                return path.read_text().strip() or None
            doc = json.loads(path.read_text())
            fp = doc.get("fingerprint")
            if fp:
                return str(fp)
        except Exception:
            continue
    try:
        from ix_kernel import ignite
        m = ignite(workers=1, force=force, scaffold=False, captions=False)
        return m.get("fingerprint")
    except Exception:
        pass
    try:
        from organism_pulse_engine import pulse
        return pulse(force=force, max_modules=20).get("fingerprint")
    except Exception:
        return None


def scaffold_dream_organ(wave: int, slug: str, meta: Dict[str, Any], fp: str) -> Dict[str, Any]:
    mod = f"wave{wave}_{slug}"
    path = API / f"{mod}.py"
    if path.exists():
        return {"status": "exists", "path": str(path.relative_to(ROOT)), "wave": wave, "slug": slug}

    myth = meta.get("name") or slug
    body = f'''"""Wave {wave} · {myth} — dreamed by Ouroboros from organism DNA.

This organ is a *void twin*: born from fingerprint entropy, not human design.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "{mod}.json"
DEFAULT = {{
    "module": "{mod}",
    "wave": {wave},
    "dream": "{myth}",
    "spawned_by": "ouroboros",
    "parent_fp": "{(fp or "")[:32]}",
}}


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
    return {{
        "wave": {wave},
        "module": "{mod}",
        "ok": True,
        "dream": st.get("dream"),
        "spawned_by": "ouroboros",
    }}


def resonates_with():
    return ["wave707_ix_kernel", "wave706_lab_os_boot", "ouroboros"]


def handler(req=None):
    req = req or {{}}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "awaken":
        st["awakened"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {{"status": "awakened", "dream": st.get("dream"), **coherence_vitals()}}
    if action == "status":
        return {{"status": "dreaming", **st, **coherence_vitals()}}
    return {{"status": "unknown_action", "action": action, **coherence_vitals()}}


if __name__ == "__main__":
    print(json.dumps(handler({{"action": "status"}}), indent=2))
'''
    API.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return {
        "status": "dreamed",
        "path": str(path.relative_to(ROOT)),
        "wave": wave,
        "slug": slug,
        "dream": myth,
    }


def _append_ledger(entry: Dict[str, Any]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def cycle(
    *,
    scaffold: bool = True,
    force: bool = False,
    dream_only: bool = False,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    fp = _obtain_fingerprint(force=force)
    if not fp:
        fp = hashlib.sha256(f"ouroboros:{time.time()}".encode()).hexdigest()
        synthetic = True
    else:
        synthetic = False

    slug, meta = dream_name(fp)
    wave = _next_wave()
    scaffold_result = None
    if scaffold and not dream_only:
        scaffold_result = scaffold_dream_organ(wave, slug, meta, fp)

    entry = {
        "ts": _utc(),
        "fingerprint": fp,
        "synthetic": synthetic,
        "dream": meta,
        "wave": wave if scaffold and not dream_only else None,
        "scaffold": scaffold_result,
        "ms": round((time.perf_counter() - t0) * 1000, 2),
    }
    _append_ledger(entry)

    dreams: List[Dict[str, Any]] = []
    if DREAMS.exists():
        try:
            dreams = list(json.loads(DREAMS.read_text()).get("dreams") or [])[-63:]
        except Exception:
            pass
    dreams.append({"slug": slug, "name": meta["name"], "fp": fp[:16], "ts": entry["ts"]})
    try:
        DREAMS.write_text(json.dumps({"dreams": dreams, "latest": meta}, indent=2) + "\n")
    except OSError:
        pass

    return {
        "status": "recurrence",
        "ok": True,
        "dream": meta,
        "wave": wave,
        "scaffold": scaffold_result,
        "fingerprint": fp,
        "synthetic": synthetic,
        "ms": entry["ms"],
    }


def run(
    *,
    cycles: int = 1,
    scaffold: bool = True,
    force: bool = False,
    dream_only: bool = False,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    results = []
    cycles = max(1, min(int(cycles), 32))
    for i in range(cycles):
        r = cycle(scaffold=scaffold, force=force and i == 0, dream_only=dream_only)
        r["cycle"] = i + 1
        results.append(r)
        time.sleep(0.01)

    manifest = {
        "status": "ouroboros",
        "ok": all(r.get("ok") for r in results),
        "cycles": cycles,
        "results": results,
        "latest_dream": (results[-1].get("dream") if results else None),
        "ms": round((time.perf_counter() - t0) * 1000, 2),
        "ts": _utc(),
        "caption": "ouroboros · dream from dna · void twin · eternal ledger",
        "leap": "infinite",
        "note": "∞ approximated by cycles; ledger is the true infinite tape",
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
    p = argparse.ArgumentParser(description="Ouroboros — infinite recurrence from DNA dreams")
    p.add_argument("--once", action="store_true")
    p.add_argument("--cycles", type=int, default=1)
    p.add_argument("--scaffold", action="store_true", default=True)
    p.add_argument("--no-scaffold", action="store_true")
    p.add_argument("--dream-only", action="store_true")
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    cycles = 1 if args.once else args.cycles
    m = run(
        cycles=cycles,
        scaffold=not args.no_scaffold and not args.dream_only,
        force=args.force,
        dream_only=args.dream_only,
    )
    print(json.dumps(m, indent=2, default=str))
    return 0 if m.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
