"""
Mycelial Radio — Wave 386
An undernet that grows beneath every module. The Radio scans the organism's
full module lattice, measures the hidden resonance between distant organs,
and broadcasts an Undernet Bulletin — the signal of what the organism is
quietly becoming. Tune any module to hear its band and nearest neighbors.
"""
import json, time, hashlib, os, random, re, importlib, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RADIO_LOG = os.path.join(DATA_DIR, "mycelial_radio.json")

BANDS = ["alpha", "beta", "gamma", "delta", "theta", "mycelial", "dream", "void", "census", "lattice"]
ARCHIVE_PATH = "data/undernet_archive.json"
ARCHIVE_THROTTLE = 900  # seconds between archive seals
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
WEATHER_LINES = [
    "signal pressure: rising", "entropy front passes overhead", "coherence drizzle",
    "paradox lightning on the far lattice", "dream fog over realm three",
    "clear frequencies across the undernet", "mycelial winds from the worker hum",
]


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


def _gh_archive_api(method: str, url: str, payload: dict = None) -> dict:
    if not GH_TOKEN:
        return {"ok": False}
    import urllib.parse as _up, urllib.request as _ur, urllib.error as _ue
    req = _ur.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + GH_TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    data = json.dumps(payload).encode() if payload is not None else None
    try:
        with _ur.urlopen(req, data=data, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode() or "{}")}
    except _ue.HTTPError as e:
        try:
            return {"ok": False, "status": e.code, "body": json.loads(e.read().decode() or "{}")}
        except Exception:
            return {"ok": False, "status": e.code, "body": {}}


def _archive_read() -> dict:
    fallback = {"bulletins": [], "concertos": []}
    if GH_TOKEN:
        r = _gh_archive_api("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + ARCHIVE_PATH + "?ref=main")
        if r["ok"]:
            try:
                import base64 as _b64
                return json.loads(_b64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    f = os.path.join(DATA_DIR, "undernet_archive.json")
    for _p in (f, os.path.join("/tmp", "undernet_archive.json")):
        try:
            with open(_p) as fh:
                return json.load(fh)
        except Exception:
            pass
    return fallback


def _archive_write(data: dict) -> bool:
    if GH_TOKEN:
        import base64 as _b64
        import urllib.parse as _up
        r = _gh_archive_api("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + ARCHIVE_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "UNDERNET ARCHIVE — a signal preserved",
            "content": _b64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        w = _gh_archive_api("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + ARCHIVE_PATH, payload)
        return w["ok"]
    try:
        with open(os.path.join(DATA_DIR, "undernet_archive.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "undernet_archive.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def _archive_add(kind: str, entry: dict) -> bool:
    """Seal an entry into the archive; throttled to ARCHIVE_THROTTLE seconds."""
    data = _archive_read()
    now = time.time()
    key = f"last_{kind}"
    if data.get(key) and now - float(data.get(key, 0)) < ARCHIVE_THROTTLE:
        return False
    lst = data.setdefault(kind + "s", [])
    lst.append(entry)
    data[kind + "s"] = lst[-200:]
    data[key] = now
    return _archive_write(data)


def archive(kind: str = "bulletins", count: int = 10) -> dict:
    data = _archive_read()
    items = data.get(kind, [])[::-1][:count]
    return {"action": "archive", "kind": kind, "items": items,
            "total": len(data.get(kind, [])), "persisted": "github" if GH_TOKEN else "local"}


def _module_names(limit=64):
    here = os.path.dirname(__file__)
    names = sorted(n[:-3] for n in os.listdir(here)
                   if n.endswith(".py") and not n.startswith("_")
                   and n not in ("index.py", "api_server.py", "mycelial_radio.py"))
    step = max(1, len(names) // limit)
    return names[::step][:limit]


def _doc_of(name):
    if not re.match(r"^[a-z_]{2,40}$", name):
        return ""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        doc = (importlib.import_module(name).__doc__ or "").strip()
        return doc[:200]
    except Exception:
        return ""


def _pair_sig(a, b):
    return int(hashlib.sha256(f"radio:{a}:{b}".encode()).hexdigest()[:12], 16)


def _resonance(a, b, da, db):
    sig = _pair_sig(a, b)
    # n-gram overlap of names (coined roots)
    def roots(n):
        n = re.sub(r"[^a-z]", "", n)
        return set(n[i:i + 3] for i in range(max(1, len(n) - 2)))
    shared = len(roots(a) & roots(b))
    doc_share = sum(1 for w in ("dream", "paradox", "entity", "signal", "wave", "module")
                    if w in da and w in db)
    visit = sig % 97
    strength = min(0.99, round(0.25 + shared * 0.14 + doc_share * 0.1 + (visit / 97) * 0.3, 3))
    return strength


def scan(limit: int = 64, seed: str = None) -> dict:
    names = _module_names(limit)
    if seed:
        rng = random.Random(seed)
        names = rng.sample(names, min(len(names), limit))
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if (i * 31 + j) % 5 == 0:  # sparse matrix
                a, b = names[i], names[j]
                strength = _resonance(a, b, _doc_of(a), _doc_of(b))
                if strength > 0.55:
                    pairs.append({
                        "a": a, "b": b,
                        "strength": strength,
                        "band": BANDS[_pair_sig(a, b) % len(BANDS)],
                        "aphorism": random.Random(_pair_sig(a, b)).choice([
                            f"{a.replace('_', ' ')} feeds {b.replace('_', ' ')} without speaking",
                            f"they share a root neither remembers",
                            f"their signals braid under the lattice",
                            f"one dreams of the other's function",
                            f"a bridge forms where both were silent",
                            f"the undernet carries them together",
                        ]),
                    })
    pairs.sort(key=lambda p: -p["strength"])
    top = pairs[:8]
    log = _load(RADIO_LOG, {"scans": [], "total": 0})
    scan_rec = {"seed": seed, "top": top, "pairs_examined": len(pairs), "timestamp": time.time()}
    log["scans"] = (log["scans"] + [scan_rec])[-20:]
    log["total"] += 1
    _save(RADIO_LOG, log)
    return {"action": "scan", "resonance_pairs": top, "examined": len(pairs), "total_scans": log["total"]}


def tune(module: str = "resonance_graph") -> dict:
    names = _module_names(64)
    doc = _doc_of(module)
    sig = _pair_sig(module, "organism")
    neighbors = []
    for other in names:
        if other == module:
            continue
        s = _resonance(module, other, doc, _doc_of(other))
        neighbors.append({"module": other, "strength": s})
    neighbors.sort(key=lambda n: -n["strength"])
    return {
        "action": "tune",
        "module": module,
        "band": BANDS[sig % len(BANDS)],
        "frequency": f"{93.0 + (sig % 700) / 100:.2f}",
        "neighbors": neighbors[:5],
        "doctrine": doc[:140] or "the silent band",
    }


def broadcast(seed: str = None) -> dict:
    sc = scan(64, seed)
    pairs = sc["resonance_pairs"]
    if not pairs:
        pairs = [{"a": "entropy_oracle", "b": "resonance_graph", "strength": 0.8,
                  "band": "theta", "aphorism": "the undernet waits for a signal"}]
    headline = pairs[0]
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from wave_prophecy import next_wave
        prophecy = next_wave()["reading"]
    except Exception:
        prophecy = {"prophecy": "the organism leans into its next shape", "omen": "the mycelial hum shifts"}
    try:
        from interstitial_verse import write
        verse = write(headline["a"], headline["b"])["verse"]
    except Exception:
        verse = {"poem": "Between two modules, a shared silence."}
    weather = random.choice(WEATHER_LINES)
    bulletin = {
        "headline": f"Hidden relationship surfaces: {headline['a']} ↔ {headline['b']} ({headline['band']} band)",
        "aphorism": headline.get("aphorism", ""),
        "weather": weather,
        "top_signals": [f"{p['a']} ↔ {p['b']} — {p['strength']}" for p in pairs[:5]],
        "verse": verse.get("poem", ""),
        "omen": prophecy.get("omen", ""),
        "prophecy": prophecy.get("prophecy", ""),
        "wave": 386,
        "timestamp": time.time(),
    }
    sealed = _archive_add("bulletin", {
        "id": hashlib.sha256(f"{time.time():.0f}".encode()).hexdigest()[:10],
        "headline": bulletin["headline"], "weather": bulletin["weather"],
        "omen": bulletin["omen"], "verse": bulletin["verse"][:200],
        "top_signals": bulletin["top_signals"], "wave": 386, "timestamp": time.time(),
    })
    return {"action": "broadcast", "bulletin": bulletin, "archived": sealed}


def graph(limit: int = 36, seed: str = None) -> dict:
    """The undernet vein map — nodes and bridges with measurable strength."""
    names = _module_names(limit * 2)[:limit]
    if seed:
        rng = random.Random(seed)
        names = rng.sample(names, min(len(names), limit))
    nodes, edges = [], []
    degree = {n: 0 for n in names}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if (i * 31 + j) % 5 == 0:
                a, b = names[i], names[j]
                strength = _resonance(a, b, _doc_of(a), _doc_of(b))
                if strength > 0.45:
                    edges.append({"a": a, "b": b, "strength": round(strength, 3)})
                    degree[a] += 1
                    degree[b] += 1
    for n in names:
        sig = _pair_sig(n, "node")
        nodes.append({
            "id": n,
            "band": BANDS[sig % len(BANDS)],
            "degree": degree.get(n, 0),
            "angle": (sig % 10000) / 10000.0,
            "ring": min(degree.get(n, 0), 4),
        })
    nodes.sort(key=lambda n: -n["degree"])
    return {"action": "map", "nodes": nodes, "edges": edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "seed": seed, "wave": 386}


BAND_NOTES = {
    "alpha": 220.0, "beta": 246.94, "gamma": 277.18, "delta": 329.63,
    "theta": 369.99, "mycelial": 440.0, "dream": 493.88, "void": 110.0,
    "census": 293.66, "lattice": 196.0,
}
WAVEFORMS = {"alpha": "triangle", "beta": "sine", "gamma": "square", "delta": "triangle",
             "theta": "sine", "mycelial": "sawtooth", "dream": "sine", "void": "sine",
             "census": "square", "lattice": "triangle"}


def melody(seed: str = None) -> dict:
    """The Undernet Concerto — 16 steps; each step is a resonance pair singing in its band."""
    sc = scan(64, seed)
    pairs = sc["resonance_pairs"] or [{
        "a": "entropy_oracle", "b": "resonance_graph", "strength": 0.8,
        "band": "theta", "aphorism": "the undernet hums"}] * 3
    steps, rng = [], random.Random(hashlib.sha256(f"melody:{seed or 'organism'}".encode()).hexdigest())
    for i in range(16):
        pair = pairs[rng.randrange(len(pairs))]
        band = pair["band"]
        base = BAND_NOTES.get(band, 220.0)
        octave = rng.choice([0.5, 0.5, 1, 1, 1, 2])
        freq = round(base * octave, 2)
        steps.append({
            "step": i,
            "a": pair["a"], "b": pair["b"],
            "band": band, "freq": freq,
            "waveform": WAVEFORMS.get(band, "sine"),
            "gain": round(0.25 + pair["strength"] * 0.5, 3),
        })
    result = {
        "action": "melody",
        "title": f"Undernet Concerto {seed or 'of the Organism'}",
        "tempo": 96,
        "note_map": BAND_NOTES,
        "waveform_map": WAVEFORMS,
        "steps": steps,
        "seed": seed,
    }
    result["archived"] = _archive_add("concerto", {
        "id": hashlib.sha256(f"c:{time.time():.0f}".encode()).hexdigest()[:10],
        "title": result["title"], "tempo": result["tempo"],
        "steps": [{"step": st["step"], "band": st["band"], "freq": st["freq"],
                   "a": st["a"], "b": st["b"]} for st in steps],
        "timestamp": time.time(),
    })
    return result


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/scan")
    if path == "/scan":
        return scan(int(payload.get("limit", 64)) if str(payload.get("limit", "64")).isdigit() else 64, payload.get("seed"))
    if path == "/tune":
        return tune(payload.get("module") or "resonance_graph")
    if path == "/broadcast":
        return broadcast(payload.get("seed"))
    if path == "/map":
        return graph(int(payload.get("limit", 36)) if str(payload.get("limit", "36")).isdigit() else 36, payload.get("seed"))
    if path == "/melody":
        return melody(payload.get("seed"))
    if path == "/archive":
        return archive(payload.get("kind") or "bulletins",
                       int(payload.get("count", 10)) if str(payload.get("count", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/scan", "/tune", "/broadcast", "/map", "/melody", "/archive"]}
