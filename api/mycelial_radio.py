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
    return {"action": "broadcast", "bulletin": bulletin}


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
    return {"error": "unknown", "available": ["/scan", "/tune", "/broadcast", "/map"]}
