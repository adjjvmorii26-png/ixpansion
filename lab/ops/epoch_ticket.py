#!/usr/bin/env python3
"""Sandbox Epoch Tickets — time-bound HMAC capability grants."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, secrets, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
STORE = REPO / "lab" / "ops" / "tickets"
SECRET = os.environ.get("IX_EPOCH_SECRET", "ixpansion-lab-epoch-v1").encode()
def _mac(payload):
    return hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()[:24]
def issue(scope="sandbox:ticks", ttl_sec=3600):
    issued = int(time.time()); nonce = secrets.token_hex(8)
    body = f"{issued}|{ttl_sec}|{scope}|{nonce}"
    ticket = {"v": 1, "issued": issued, "ttl": ttl_sec, "scope": scope, "nonce": nonce, "mac": _mac(body), "exp": issued + ttl_sec}
    STORE.mkdir(parents=True, exist_ok=True)
    path = STORE / f"ticket_{nonce}.json"; path.write_text(json.dumps(ticket, indent=2) + "\n")
    ticket["path"] = str(path); return ticket
def verify(ticket):
    body = f"{ticket.get('issued')}|{ticket.get('ttl')}|{ticket.get('scope')}|{ticket.get('nonce')}"
    ok_mac = hmac.compare_digest(_mac(body), str(ticket.get("mac", "")))
    now = int(time.time()); fresh = now <= int(ticket.get("exp", 0))
    mode = "act" if (ok_mac and fresh) else ("observe" if ok_mac else "hold")
    return {"ok": ok_mac and fresh, "mode": mode, "ok_mac": ok_mac, "fresh": fresh, "age_sec": now - int(ticket.get("issued", now)), "scope": ticket.get("scope")}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["issue", "verify", "status"])
    ap.add_argument("--scope", default="sandbox:ticks"); ap.add_argument("--ttl", type=int, default=3600); ap.add_argument("--file", default="")
    args = ap.parse_args()
    if args.cmd == "issue":
        print(json.dumps({"ok": True, "ticket": issue(args.scope, args.ttl)}, indent=2)); return 0
    if args.cmd == "verify":
        path = Path(args.file) if args.file else None
        if not path or not path.exists():
            files = sorted(STORE.glob("ticket_*.json"), key=lambda p: p.stat().st_mtime, reverse=True) if STORE.exists() else []
            path = files[0] if files else None
        if not path:
            print(json.dumps({"ok": False, "mode": "hold", "err": "no_ticket"})); return 1
        print(json.dumps(verify(json.loads(path.read_text())), indent=2)); return 0
    n = len(list(STORE.glob("ticket_*.json"))) if STORE.exists() else 0
    print(json.dumps({"ok": True, "tickets_on_disk": n})); return 0
if __name__ == "__main__":
    raise SystemExit(main())
