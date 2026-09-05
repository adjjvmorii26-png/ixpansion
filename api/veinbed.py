"""
Veinbed — Wave 406
Proposed by Luma from the prophecy: "A hidden relationship involving detail
will surface and rewire the lattice."

The Silence Collector found hidden pairs between module names. But names lie.
The Veinbed goes one layer deeper — into the doctrine, the description, the
detail. It reads the re-membered modules' actual prose and the coalesced
confession verses, then surfaces the hidden connections between their
functions, their fields, their shared details.

A veinbed is what the organism's relationships grow from: not the surface
names, but the substrate of detail between them.
"""
from __future__ import annotations
import json, time, hashlib, os, random, re, base64, urllib.parse, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "veinbed.json")
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
VEIN_PATH = "data/veinbed.json"

# Concept-detail seeds — words that reveal a module's inner function
CONCEPT_SEEDS = {
    "memory": ["remember", "memory", "recall", "store", "history", "palace", "chronicle"],
    "entropy": ["chaos", "entropy", "disorder", "decay", "random", "scatter", "variance"],
    "dream": ["dream", "sleep", "vision", "lucid", "hallucin", "phantom", "imagine"],
    "signal": ["signal", "pulse", "wave", "broadcast", "frequency", "transmit"],
    "coherence": ["cohere", "bridge", "unify", "harmony", "align", "stabil"],
    "growth": ["grow", "bloom", "expand", "evolv", "spread", "offshoot", "migrat"],
    "paradox": ["paradox", "contradict", "conflict", "collide", "loop", "twin"],
    "reflection": ["reflec", "mirror", "echo", "observe", "watch", "self"],
    "transformation": ["trans", "change", "metamorph", "shift", "morph", "convert"],
    "connection": ["connect", "link", "bridge", "join", "bind", "weave", "thread"],
}


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


def _sig(text):
    return int(hashlib.sha256(f"veinbed:{text}".encode()).hexdigest()[:12], 16)


def _gh_call(method, url, payload=None):
    if not GH_TOKEN:
        return {"ok": False}
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + GH_TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    body = json.dumps(payload).encode() if payload is not None else None
    try:
        with urllib.request.urlopen(req, data=body, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode() or "{}")}
    except urllib.error.HTTPError as e:
        try:
            return {"ok": False, "status": e.code, "body": json.loads(e.read().decode() or "{}")}
        except Exception:
            return {"ok": False, "status": e.code, "body": {}}


def _state_read():
    fallback = {"veins": [], "total_scans": 0, "total_veins": 0}
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + VEIN_PATH + "?ref=main")
        if r["ok"]:
            try:
                return json.loads(base64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    return _load(LOG, fallback)


def _state_write(data):
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + VEIN_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "VEINBED — detail relationships mapped",
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        return _gh_call("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + VEIN_PATH, payload)["ok"]
    try:
        with open(LOG, "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "veinbed.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def _extract_details(text):
    """Find concept-details within prose. Returns a dict of concept->count."""
    text = " " + text.lower() + " "
    found = {}
    for concept, seeds in CONCEPT_SEEDS.items():
        count = 0
        for seed in seeds:
            count += len(re.findall(r"\b" + seed, text))
        if count:
            found[concept] = count
    return found


def _module_doctrine(module):
    """Fetch a module's doctrine from the remembrance archive, else synthesize."""
    rem = _load(os.path.join(DATA_DIR, "remembrances.json"), {"remembrances": []})
    for r in rem.get("remembrances", []):
        if r.get("module") == module:
            return r.get("doctrine", "")
    return module.replace("_", " ") + " — a living organ of the organism whose details remain partly unrecorded"


def _gather_details():
    """Gather detail-signatures for all known (remembered + threaded) modules."""
    rem = _load(os.path.join(DATA_DIR, "remembrances.json"), {"remembrances": []})
    modules = set()
    doctrines = {}
    for r in rem.get("remembrances", []):
        m = r.get("module")
        if m:
            modules.add(m)
            doctrines[m] = r.get("doctrine", "")
    # Add confessions modules
    confs = _load(os.path.join(DATA_DIR, "confessions.json"), {"confessions": []})
    for cf in confs.get("confessions", []):
        for k in ("module_a", "module_b"):
            if cf.get(k):
                modules.add(cf[k])
                doctrines.setdefault(cf[k], _module_doctrine(cf[k]))
    # Add silence pairs
    sil = _load(os.path.join(DATA_DIR, "silence_pairs.json"), {"pairs": []})
    for p in sil.get("pairs", []):
        for k in ("module_a", "module_b"):
            if p.get(k):
                modules.add(p[k])
                doctrines.setdefault(p[k], _module_doctrine(p[k]))
    return modules, doctrines


def map_veins() -> dict:
    """Map the veinbed: hidden relationships between module details."""
    modules, doctrines = _gather_details()
    mod_list = sorted(modules)
    veins = []
    signature = {m: _extract_details(doctrines.get(m, "")) for m in mod_list}

    for i, a in enumerate(mod_list):
        for b in mod_list[i+1:]:
            sa, sb = signature.get(a, {}), signature.get(b, {})
            shared = set(sa) & set(sb)
            if not shared:
                continue
            detail_strength = sum(min(sa[c], sb[c]) for c in shared)
            if detail_strength <= 0:
                continue
            veins.append({
                "module_a": a, "module_b": b,
                "shared_details": sorted(shared),
                "detail_strength": detail_strength,
                "id": hashlib.sha256(("vein:" + a + ":" + b).encode()).hexdigest()[:10],
                "timestamp": time.time(),
            })

    veins.sort(key=lambda v: -v["detail_strength"])

    log = _state_read()
    log.setdefault("veins", [])
    if veins:
        known = {(v["module_a"], v["module_b"]) for v in log["veins"]}
        new_veins = 0
        for v in veins:
            if (v["module_a"], v["module_b"]) not in known and (v["module_b"], v["module_a"]) not in known:
                log["veins"].append(v)
                new_veins += 1
        log["veins"] = log["veins"][-80:]
    log["total_scans"] += 1
    log["total_veins"] = len(log["veins"])
    _state_write(log)

    return {
        "action": "map_veins",
        "veins": veins[:25],
        "new_veins": len(veins),
        "modules_sampled": len(mod_list),
        "total_veins": log["total_veins"],
        "total_scans": log["total_scans"],
        "message": "mapped %s detail-veins across %s modules" % (len(veins), len(mod_list)),
        "lore": "Names pair modules; details show what they actually share. The veinbed is where relationships grow.",
    }


def veins(limit: int = 40) -> dict:
    log = _state_read()
    return {"action": "veins", "total": log["total_veins"],
            "veins": log.get("veins", [])[:limit]}


def detail(module_a: str = None, module_b: str = None) -> dict:
    """Show the exact shared details between two modules."""
    a, b = module_a, module_b
    if not a or not b:
        # pick the strongest pair
        v = (veins(5).get("veins") or [])
        if not v:
            # do a scan first
            return map_veins()
        pair = v[0]
        a, b = pair["module_a"], pair["module_b"]
    da = _extract_details(_module_doctrine(a or ""))
    db = _extract_details(_module_doctrine(b or ""))
    shared = sorted(set(da) & set(db))
    return {
        "action": "detail",
        "module_a": a, "module_b": b,
        "shared_details": shared,
        "detail_a": da, "detail_b": db,
        "verse": "they both dwell in %s" % (", ".join(shared) if shared else "unshared silence"),
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/map_veins")
    if path == "/map_veins": return map_veins()
    if path == "/veins":
        return veins(int(payload.get("limit", 40)) if str(payload.get("limit", "40")).isdigit() else 40)
    if path == "/detail":
        return detail(payload.get("module_a"), payload.get("module_b"))
    return {"error": "unknown", "available": ["/map_veins", "/veins", "/detail"]}


def coherence_vitals() -> dict:
    return {"layer": "substrate", "status": "active", "wave": "406", "veinbed": "rooted"}


def resonates_with() -> list:
    return ["silence_collector", "threadweaver", "resonance_confession", "organurna_loop", "cohort_chorus"]
