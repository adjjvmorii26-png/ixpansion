"""
Ouroboros Ledger — Wave 381
The organism seals every evolution into a chain of hashes — a self-verifying
timechain of waves. Each seal binds the current commit to the last seal, so
the organism's history cannot be silently rewritten: the ledger would fracture.
"""
import json, time, hashlib, os, subprocess, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LEDGER = os.path.join(DATA_DIR, "ouroboros.json")

GENESIS = "GENESIS_WAVE_000"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _git_head() -> dict:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip()
        msg = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=5).stdout.strip()
        m = re.search(r"WAVE\s*(\d+)", msg.upper())
        wave = int(m.group(1)) if m else 381
        return {"sha": sha or "unknown", "message": msg or "no commit", "wave": wave}
    except Exception:
        return {"sha": "unknown", "message": "no commit", "wave": 381}


def seal() -> dict:
    head = _git_head()
    ledger = _load(LEDGER, {"chain": [], "total": 0})
    chain = ledger.get("chain", [])
    prev = chain[-1]["hash"] if chain else GENESIS
    raw = f"{head['wave']}:{head['sha']}:{prev}:{time.time():.0f}"
    seal_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    block = {
        "wave": head["wave"],
        "commit": head["sha"],
        "message": head["message"],
        "prev": prev,
        "hash": seal_hash,
        "sealed_at": time.time(),
    }
    # do not duplicate the same commit twice
    if not chain or chain[-1].get("commit") != head["sha"]:
        chain.append(block)
        chain = chain[-200:]
        ledger["chain"] = chain
        ledger["total"] = len(chain)
        _save(LEDGER, ledger)
    return {"action": "seal", "block": block, "chain_length": len(chain)}


def chain() -> dict:
    ledger = _load(LEDGER, {"chain": []})
    chain = ledger.get("chain", [])
    # verify integrity
    valid = True
    prev = GENESIS
    for i, b in enumerate(chain):
        if b["prev"] != prev:
            valid = False
            break
        prev = b["hash"]
        recomputed = hashlib.sha256(f"{b['wave']}:{b['commit']}:{b['prev']}:{int(b['sealed_at']):d}".encode()).hexdigest()[:16]
        if recomputed != b["hash"]:
            valid = False
            break
    return {"action": "chain", "length": len(chain), "valid": valid, "blocks": chain[::-1][:20], "genesis": GENESIS}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/chain")
    if path == "/seal":
        return seal()
    if path == "/chain":
        return chain()
    return {"error": "unknown", "available": ["/seal", "/chain"]}
