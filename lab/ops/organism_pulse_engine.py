#!/usr/bin/env python3
"""Organism Pulse Engine — unique fast path for organism-wide data.

Solution:
  1. Path-index — discover wave*.py by filesystem only
  2. Bloom strip — O(1) membership
  3. Lazy vitals — cache by mtime
  4. XOR fingerprint — 256-bit organism DNA
  5. Delta gate — skip work if unchanged
  6. workers + isolate_dirty — parallel + subprocess for dirty modules
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "api"
DATA = ROOT / "data"
CACHE_FILE = DATA / "organism_pulse_cache.json"
FP_FILE = DATA / "organism_fingerprint.hex"

BLOOM_BITS = 1024

DIRTY_SUBSTRINGS = (
    "coherence_regulator",
    "wave190", "wave191", "wave192", "wave193",
    "wave194", "wave195", "wave196", "wave197",
)


def _wave_paths() -> List[Path]:
    if not API.is_dir():
        return []
    return sorted(API.glob("wave*.py"))


def build_index() -> Dict[str, Any]:
    paths = _wave_paths()
    by_num: Dict[int, str] = {}
    bloom = [0] * BLOOM_BITS
    for p in paths:
        name = p.stem
        parts = name.split("_", 1)
        if len(parts) < 1 or not parts[0].startswith("wave"):
            continue
        num_s = parts[0][4:]
        if not num_s.isdigit():
            continue
        n = int(num_s)
        by_num[n] = str(p.relative_to(ROOT))
        bloom[n % BLOOM_BITS] = 1
    return {
        "count": len(by_num),
        "waves": sorted(by_num.keys()),
        "paths": by_num,
        "bloom": bloom,
        "ts": time.time(),
    }


def bloom_has(index: Dict[str, Any], wave: int) -> bool:
    bloom = index.get("bloom") or []
    if not bloom:
        return wave in (index.get("paths") or {})
    if not bloom[wave % BLOOM_BITS]:
        return False
    return wave in (index.get("paths") or {})


def _load_module(path: Path):
    mod_name = f"pulse_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


def vitals_one(path: Path) -> Optional[Dict[str, Any]]:
    mod = _load_module(path)
    if mod is None:
        return None
    fn = getattr(mod, "coherence_vitals", None)
    if not callable(fn):
        return {"module": path.stem, "ok": False, "error": "no_vitals"}
    try:
        v = fn()
        if isinstance(v, dict):
            v.setdefault("module", path.stem)
            return v
    except Exception as e:
        return {"module": path.stem, "ok": False, "error": type(e).__name__}
    return None


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _load_cache() -> Dict[str, Any]:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            pass
    return {"entries": {}, "fp": None}


def _save_cache(cache: Dict[str, Any]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = CACHE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(cache, indent=2) + "\n")
        tmp.replace(CACHE_FILE)
    except OSError:
        pass


def fingerprint(vitals_list: List[Dict[str, Any]]) -> str:
    acc = bytearray(32)
    for v in sorted(vitals_list, key=lambda x: str(x.get("module") or x.get("wave") or "")):
        digest = hashlib.sha256(
            json.dumps(v, sort_keys=True, default=str).encode()
        ).digest()
        for i, b in enumerate(digest):
            acc[i] ^= b
    return acc.hex()


def _is_dirty(path: Path) -> bool:
    return any(s in path.stem for s in DIRTY_SUBSTRINGS)


def pulse(
    *,
    force: bool = False,
    only_waves: Optional[List[int]] = None,
    max_modules: int = 200,
    workers: int = 1,
    isolate_dirty: bool = True,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    index = build_index()
    cache = _load_cache()
    entries = cache.setdefault("entries", {})

    paths_map = index.get("paths") or {}
    selected: List[Tuple[int, Path]] = []
    for n, rel in paths_map.items():
        if only_waves is not None and n not in only_waves:
            continue
        selected.append((n, ROOT / rel))
    selected.sort(key=lambda x: x[0])
    selected = selected[:max_modules]

    vitals_list: List[Dict[str, Any]] = []
    hits = 0
    misses = 0
    isolated = 0

    def _compute(path: Path) -> Dict[str, Any]:
        nonlocal isolated
        if isolate_dirty and _is_dirty(path):
            try:
                from subprocess_vitals import vitals_isolated
                isolated += 1
                return vitals_isolated(path)
            except Exception:
                return vitals_one(path) or {"ok": False, "module": path.stem, "error": "iso_fail"}
        return vitals_one(path) or {"ok": False, "module": path.stem, "error": "none"}

    to_compute: List[Tuple[str, float, Path]] = []
    for n, path in selected:
        key = str(path.relative_to(ROOT))
        mt = _mtime(path)
        cached = entries.get(key)
        if (
            not force
            and isinstance(cached, dict)
            and cached.get("mtime") == mt
            and isinstance(cached.get("vitals"), dict)
        ):
            vitals_list.append(cached["vitals"])
            hits += 1
            continue
        to_compute.append((key, mt, path))

    results_map = {}
    if workers > 1 and len(to_compute) > 1:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=min(workers, 4)) as ex:
            futs = {ex.submit(_compute, path): (key, mt, path) for key, mt, path in to_compute}
            for fut in as_completed(futs):
                key, mt, path = futs[fut]
                try:
                    v = fut.result()
                except Exception as e:
                    v = {"ok": False, "module": path.stem, "error": type(e).__name__}
                results_map[key] = (mt, v)
    else:
        for key, mt, path in to_compute:
            results_map[key] = (mt, _compute(path))

    for key, mt, path in to_compute:
        mt2, v = results_map[key]
        if v is None:
            misses += 1
            continue
        entries[key] = {"mtime": mt2, "vitals": v}
        vitals_list.append(v)
        misses += 1

    fp = fingerprint(vitals_list)
    prev_fp = cache.get("fp")
    changed = fp != prev_fp
    cache["fp"] = fp
    cache["entries"] = entries
    cache["last_pulse"] = time.time()
    _save_cache(cache)

    try:
        FP_FILE.write_text(fp + "\n")
    except OSError:
        pass

    ms = round((time.perf_counter() - t0) * 1000, 2)
    ok_n = sum(1 for v in vitals_list if v.get("ok", True) and "error" not in v)
    return {
        "status": "pulse",
        "modules_indexed": index["count"],
        "modules_pulsed": len(vitals_list),
        "ok": ok_n,
        "cache_hits": hits,
        "computed": misses,
        "fingerprint": fp,
        "changed": changed,
        "ms": ms,
        "waves": index.get("waves") or [],
        "bloom_popcount": sum(index.get("bloom") or []),
        "workers": workers,
        "isolated": isolated,
    }


def pulse_range(lo: int, hi: int, **kw) -> Dict[str, Any]:
    return pulse(only_waves=list(range(lo, hi + 1)), **kw)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(argv or sys.argv[1:])
    force = "--force" in argv
    if "--range" in argv:
        i = argv.index("--range")
        lo, hi = int(argv[i + 1]), int(argv[i + 2])
        out = pulse_range(lo, hi, force=force)
    else:
        out = pulse(force=force)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
