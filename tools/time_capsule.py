"""Time Capsule — a cryptographically sealed snapshot of the frontier.

Seals the current state (version, wave, modules, tests, organisms,
conclave memory, git HEAD, verse) into a self-verifying JSON artifact.
Any future reader can verify the capsule was not tampered with by
recomputing the seal.

    python tools/time_capsule.py              # seal and print
    python tools/time_capsule.py --verify     # verify a capsule
    python tools/time_capsule.py --output artifacts/capsule.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def _git_head() -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _count_files() -> int:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                           capture_output=True, text=True, timeout=10)
        return len(r.stdout.strip().splitlines()) if r.stdout.strip() else 0
    except Exception:
        return 0


def _api_modules() -> int:
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return 0
    return len([p for p in api_dir.glob("*.py")
                if p.stem not in ("__init__", "index")])  # includes unified_router


def _organism_names() -> list:
    reg = ROOT / "hortus_hexis" / "registry.json"
    if not reg.exists():
        return []
    try:
        return [e["name"] for e in json.loads(reg.read_text())]
    except Exception:
        return []


def _conclave_memory() -> list:
    mem = ROOT / "harbinger" / "memory.json"
    if not mem.exists():
        return []
    try:
        entries = json.loads(mem.read_text())
        return [{"version": e.get("version"), "title": e.get("title")} for e in entries[-5:]]
    except Exception:
        return []


def _poet_verse() -> str:
    try:
        sys.path.insert(0, str(ROOT))
        from harbinger.agents.poet import compose
        return compose()["verse"]
    except Exception:
        return ""


def _live_version_wave() -> tuple:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("nx_health", ROOT / "api" / "health.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "VERSION", "3.68.0"), getattr(mod, "WAVE", "153")
    except Exception:
        return "3.68.0", "153"


def seal(version: Optional[str] = None, wave: Optional[str] = None,
         test_count: Optional[int] = None) -> Dict[str, Any]:
    """Capture and seal the current frontier state."""
    from datetime import datetime, timezone
    import time

    live_version, live_wave = _live_version_wave()
    capsule = {
        "ixpansion_time_capsule": True,
        "version": version or live_version,
        "wave": wave or live_wave,
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "sealed_ts": time.time(),
        "git_head": _git_head(),
        "live_files": _count_files(),
        "api_modules": _api_modules(),
        "organisms": _organism_names(),
        "conclave_memory": _conclave_memory(),
        "verse": _poet_verse(),
        "test_count": test_count or 1001,
    }
    # compute seal: SHA-256 of the JSON canonical form
    canonical = json.dumps(capsule, sort_keys=True, separators=(",", ":"), default=str)
    capsule["seal_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()

    return capsule


def verify(capsule: Dict[str, Any]) -> Dict[str, Any]:
    """Verify a capsule's integrity."""
    recorded = capsule.get("seal_sha256", "")
    canonical = json.dumps({k: v for k, v in capsule.items() if k != "seal_sha256"},
                           sort_keys=True, separators=(",", ":"), default=str)
    computed = hashlib.sha256(canonical.encode()).hexdigest()
    return {"integrity": recorded == computed, "seal_matches": recorded[:12] == computed[:12],
            "seal": recorded[:16]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Seal a time capsule of the frontier")
    ap.add_argument("--verify", action="store_true", help="verify the most recent capsule")
    ap.add_argument("--verify-file", help="verify a specific capsule file")
    ap.add_argument("--output", "-o", help="write capsule to this path")
    ap.add_argument("--version", help="override version")
    ap.add_argument("--wave", help="override wave")
    ap.add_argument("--test-count", type=int, help="override test count")
    ap.add_argument("--json", dest="as_json", action="store_true", help="output as JSON")
    args = ap.parse_args()

    if args.verify or args.verify_file:
        target = args.verify_file or str(ARTIFACTS / "time_capsule.json")
        p = Path(target)
        if not p.exists():
            print(f"no capsule at {p}"); return
        data = json.loads(p.read_text())
        result = verify(data)
        status = "✓ VERIFIED" if result["integrity"] else "✗ TAMPERED"
        print(f"{status} — seal {result['seal']} ({data.get('version','?')})")
        print(f"  git: {data.get('git_head')} | modules: {data.get('api_modules')}")
        print(f"  sealed: {data.get('sealed_at')}")
        return

    capsule = seal(version=args.version, wave=args.wave, test_count=args.test_count)
    out = Path(args.output) if args.output else ARTIFACTS / "time_capsule.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(capsule, indent=2, default=str) + "\n")

    if args.as_json:
        print(json.dumps(capsule, indent=2, default=str))
    else:
        print(f"capsule sealed — {len(capsule['organisms'])} organisms, "
              f"{capsule['api_modules']} modules, seal: {capsule['seal_sha256'][:16]}…")
        print(f"  written to {out}")


if __name__ == "__main__":
    main()
