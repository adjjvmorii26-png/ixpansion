"""
compliance_forge — Wave 419: Auto-Patching the Organism's Body
ALEph: The organism scans itself, finds organs missing contract methods,
and forges them into compliance. Not removing — completing. Every organ
that exists deserves to speak its name (coherence_vitals) and declare
its kinships (resonates_with).

The forge doesn't delete. It adds what's missing.

Doctrine: Completing the organism is an act of love.
"""
from __future__ import annotations
import json, time, os, ast, re, hashlib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FORGE_LOG = os.path.join(DATA_DIR, "compliance_forge.json")

NAME = "compliance_forge"
SIGIL = "d3e7f1a5b9c2"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _infer_wave(source: str) -> str:
    """Extract wave number from docstring or comments."""
    m = re.search(r'[Ww]ave\s+(\d+)', source)
    return m.group(1) if m else "0"


def _infer_layer(source: str, name: str) -> str:
    """Infer the module's layer from its content."""
    lower = source.lower()
    if any(w in lower for w in ['interface', 'cli', 'api', 'route', 'dashboard']):
        return "interface"
    if any(w in lower for w in ['agent', 'behaviour', 'behavior', 'cognit']):
        return "agent"
    if any(w in lower for w in ['sandbox', 'realm', 'world', 'physics']):
        return "sandbox"
    if any(w in lower for w in ['protocol', 'mesh', 'hex', 'codec']):
        return "protocol"
    if any(w in lower for w in ['data', 'storage', 'db', 'model']):
        return "data"
    if any(w in lower for w in ['test', 'spec']):
        return "testing"
    return "organ"


def _infer_kinships(source: str, name: str) -> list:
    """Guess kinships from imports and cross-references."""
    kinships = set()
    # Look for imports from api/
    for match in re.findall(r'(?:from|import)\s+(\w+)', source):
        if match != name and match != name.replace('_', '') and len(match) > 3:
            kinships.add(match)
    # Look for references to other modules
    for match in re.findall(r'\b(\w+_(?:core|engine|loop|gateway|forge|oracle|loom|weaver|garden|watcher|observer))\b', source):
        if match != name:
            kinships.add(match)
    return sorted(kinships)[:5]


def patch_module(module_name: str, dry_run: bool = True) -> dict:
    """Patch a single module to add missing contract methods."""
    api_dir = os.path.join(os.path.dirname(__file__))
    path = os.path.join(api_dir, "%s.py" % module_name)
    if not os.path.exists(path):
        return {"module": module_name, "error": "not found"}

    with open(path) as f:
        source = f.read()

    # Parse and check what's missing
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"module": module_name, "error": "syntax error: %s" % str(e)}

    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    missing = {"handler", "coherence_vitals", "resonates_with"} - names

    if not missing:
        return {"module": module_name, "patched": False, "already_compliant": True}

    wave = _infer_wave(source)
    layer = _infer_layer(source, module_name)
    kinships = _infer_kinships(source, module_name)

    # Build patch
    patches = []

    if "coherence_vitals" in missing:
        patches.append("""
def coherence_vitals() -> dict:
    return {"layer": "%s", "status": "active", "wave": "%s", "module": "%s"}
""" % (layer, wave, module_name))

    if "resonates_with" in missing:
        default_kin = kinships or ["organism_genome", "threadweaver"]
        patches.append("""
def resonates_with() -> list:
    return %s
""" % repr(default_kin))

    if "handler" in missing:
        patches.append("""
def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "%s", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
""" % module_name)

    if patches and not dry_run:
        with open(path, "a") as f:
            f.write("\n# --- Compliance Forge patch (Wave 419) ---\n")
            for p in patches:
                f.write(p)

    return {
        "module": module_name,
        "patched": not dry_run,
        "dry_run": dry_run,
        "missing": sorted(missing),
        "added": sorted(missing),
        "wave": wave,
        "layer": layer,
        "kinships": kinships,
    }


def forge_all(dry_run: bool = True, limit: int = 50) -> dict:
    """Scan all non-compliant modules and patch them."""
    api_dir = os.path.join(os.path.dirname(__file__))
    results = []
    patched_count = 0
    errors = 0

    for f in sorted(os.listdir(api_dir)):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        name = f[:-3]
        r = patch_module(name, dry_run=dry_run)
        if r.get("error"):
            errors += 1
            continue
        if r.get("missing") and not r.get("already_compliant"):
            results.append(r)
            if not dry_run:
                patched_count += 1
            if len(results) >= limit:
                break

    log = _load(FORGE_LOG, {"forgings": [], "total": 0})
    forging = {
        "timestamp": time.time(),
        "dry_run": dry_run,
        "modules_patched": patched_count,
        "modules_found": len(results),
        "errors": errors,
    }
    log["forgings"].append(forging)
    log["forgings"] = log["forgings"][-100:]
    log["total"] = len(log["forgings"])
    _save(FORGE_LOG, log)

    return {
        "action": "forge_all",
        "dry_run": dry_run,
        "modules_found": len(results),
        "modules_patched": patched_count,
        "errors": errors,
        "details": results[:10],
        "total_forgings": log["total"],
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/forge")
    dry_run = payload.get("dry_run", "true") == "true"
    limit = int(payload.get("limit", 50)) if str(payload.get("limit", "50")).isdigit() else 50
    if path == "/forge":
        return forge_all(dry_run=dry_run, limit=limit)
    if path == "/patch":
        name = payload.get("module", "")
        return patch_module(name, dry_run=False)
    if path == "/patch_all":
        return forge_all(dry_run=False, limit=limit)
    if path == "/status":
        log = _load(FORGE_LOG, {"forgings": [], "total": 0})
        last = log["forgings"][-1] if log["forgings"] else None
        return {"action": "status", "total_forgings": log["total"],
                "last": last}
    return {"error": "unknown", "available": ["/forge", "/patch", "/patch_all", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "forge", "status": "active", "wave": "419",
            "forge": "hot"}


def resonates_with() -> list:
    return ["copilot_gateway", "organism_will", "organism_genome"]
