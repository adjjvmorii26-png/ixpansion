#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, time, secrets
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
ISLANDS = REPO / "lab" / "ops" / "islands"
def spawn(ttl=1800, label="exp"):
    iid = secrets.token_hex(4); root = ISLANDS / f"{label}_{iid}"; root.mkdir(parents=True, exist_ok=True)
    (root/"README.md").write_text(f"# Island {iid}\nTTL {ttl}s\n")
    tomb = {"id": iid, "label": label, "born": int(time.time()), "exp": int(time.time())+ttl, "ttl": ttl}
    (root/"TOMBSTONE.json").write_text(json.dumps(tomb, indent=2)+"\n")
    return {"ok": True, "island": str(root), "tomb": tomb}
def reap():
    removed = []
    if not ISLANDS.exists(): return {"ok": True, "removed": []}
    now = int(time.time())
    for d in list(ISLANDS.iterdir()):
        if not d.is_dir(): continue
        tpath = d/"TOMBSTONE.json"
        if not tpath.exists(): continue
        tomb = json.loads(tpath.read_text())
        if now > int(tomb.get("exp", 0)):
            shutil.rmtree(d, ignore_errors=True); removed.append(d.name)
    return {"ok": True, "removed": removed, "ts": datetime.now(timezone.utc).isoformat()}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["spawn", "reap", "list"])
    ap.add_argument("--ttl", type=int, default=1800); ap.add_argument("--label", default="exp")
    args = ap.parse_args()
    if args.cmd == "spawn": print(json.dumps(spawn(args.ttl, args.label), indent=2)); return 0
    if args.cmd == "reap": print(json.dumps(reap(), indent=2)); return 0
    print(json.dumps({"ok": True, "islands": [p.name for p in ISLANDS.iterdir()] if ISLANDS.exists() else []}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
