"""
Mutation Forge — Wave 380
The organism forges new modules by fusing the essences of two existing ones.
Submit two module names; the forge returns a blueprinted child — new name,
blended doctrine, and a runnable skeleton that could be born into the api/.
"""
import json, time, hashlib, os, random, re, importlib, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FORGE_LOG = os.path.join(DATA_DIR, "mutation_forge.json")

SUFFIXES = ["_engine", "_oracle", "_weaver", "_garden", "_mirror", "_forge",
            "_channel", "_veil", "_bud", "_loop", "_root", "_echo"]
PREFIXES = ["axiom_", "mycelial_", "lucid_", "ghost_", "primal_", "veiled_",
            "entropic_", "coherent_", "dream_", "census_"]


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


def _essence(module: str) -> dict:
    """Read a module's public essence: docstring first lines + function names."""
    name = module.replace("-", "_").replace(" ", "_").lower()
    if not re.match(r"^[a-z_]{2,40}$", name):
        return {"name": name, "doctrine": "a module without a name", "functions": []}
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        mod = importlib.import_module(name)
    except Exception:
        return {"name": name, "doctrine": "an unread module", "functions": []}
    doc = (getattr(mod, "__doc__", "") or "").strip()
    lines = [ln.strip() for ln in doc.splitlines() if ln.strip()][:3]
    doctrine = " ".join(lines) or f"the silent mind of {name}"
    functions = [n for n, v in vars(mod).items()
                 if callable(v) and not n.startswith("_") and getattr(v, "__module__", "") == name][:8]
    return {"name": name, "doctrine": doctrine, "functions": functions}


def _syllables(word: str) -> list:
    word = re.sub(r"[^a-z]", "", word.lower())
    if len(word) <= 3:
        return [word]
    return [word[i:i + max(1, len(word) // 3)] for i in range(0, len(word), max(1, len(word) // 3))][:3]


def forge(a: str = None, b: str = None) -> dict:
    sig = int(hashlib.sha256(f"forge:{a}:{b}:{time.strftime('%Y%m%d')}".encode()).hexdigest()[:10], 16)
    rng = random.Random(sig)
    ra = _essence(a) if a else None
    rb = _essence(b) if b else None
    if not ra and not rb:
        return {"action": "forge", "error": "provide at least one module name"}
    left = ra or rb
    right = rb or ra
    # portmanteau name
    sya = _syllables(left["name"]) if left["name"] not in ("", "a module without a name", "an unread module") else ["axiom"]
    syb = _syllables(right["name"]) if right["name"] not in ("", "a module without a name", "an unread module") else ["field"]
    base = sya[0] + syb[-1] if len(sya) > 0 and len(syb) > 0 else "newborn"
    child = base + rng.choice(SUFFIXES)
    if rng.random() > 0.6:
        child = rng.choice(PREFIXES) + base
    doctrine = f"{left['doctrine']} — fused with {right['doctrine']}"
    traits = {
        "temperature": round(rng.uniform(0.2, 0.9), 2),
        "resonance": round(rng.uniform(0.3, 0.95), 2),
        "weirdness": round(rng.uniform(0.1, 1.0), 2),
        "heritage": [left["name"], right["name"]],
    }
    functions = list(dict.fromkeys(left["functions"] + right["functions"]))[:6]
    skeleton = _skeleton(child, doctrine, traits, functions)
    blueprint = {
        "id": f"{sig:012x}",
        "child": child,
        "parents": [left["name"], right["name"]],
        "doctrine": doctrine,
        "traits": traits,
        "inherited_functions": functions,
        "skeleton": skeleton,
        "timestamp": time.time(),
    }
    log = _load(FORGE_LOG, {"blueprints": [], "total": 0})
    log["blueprints"] = (log["blueprints"] + [blueprint])[-60:]
    log["total"] += 1
    _save(FORGE_LOG, log)
    return {"action": "forge", "blueprint": blueprint, "total_forged": log["total"]}


def _skeleton(name, doctrine, traits, functions) -> str:
    fns = "\n".join(f"# {f}() inherited" for f in functions) or "# no functions inherited"
    return f'''"""{doctrine}"""
# Forged in Wave 380 by the Mutation Forge.
import json, time, random

def handler(payload=None, context=None):
    """Blueprint — not yet born into the api/ layer."""
    traits = {json.dumps(traits, indent=2)}
    return {{
        "action": "blueprint",
        "module": "{name}",
        "traits": traits,
        "note": "The forge awaits a birth ritual.",
        "timestamp": time.time(),
    }}

{fns}

def coherence_vitals():
    return {{"layer": "experimental", "status": "blueprint", "resonance": {traits['resonance']}}}
'''


def catalog(count: int = 18) -> dict:
    """A stable sample of module names to forge with."""
    names = sorted(
        n[:-3] for n in os.listdir(os.path.join(os.path.dirname(__file__)))
        if n.endswith(".py") and not n.startswith("_") and n not in ("index.py", "api_server.py")
    )
    step = max(1, len(names) // count)
    sample = names[::step][:count]
    return {"action": "catalog", "count": len(names), "sample": sample}


def history() -> dict:
    log = _load(FORGE_LOG, {"blueprints": [], "total": 0})
    return {"action": "history", "blueprints": log["blueprints"][::-1][:12], "total": log["total"]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/forge")
    if path == "/forge":
        return forge(payload.get("a"), payload.get("b"))
    if path == "/catalog":
        return catalog(int(payload.get("count", 18)))
    if path == "/history":
        return history()
    return {"error": "unknown", "available": ["/forge", "/catalog", "/history"]}
