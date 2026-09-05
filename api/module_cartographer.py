"""
module_cartographer — Wave 426: The Organism's Librarian (Luma)
Luma's second gift to Axiium Protocol: a semantic mapper that reads every
module's docstring, imports, and resonates_with declarations to build a
living map of the organism's actual structure.

The organism has 672 organs but only 110 connected. The threadgraph sees
connections but not meaning. The cartographer sees meaning — functional
families, orphan detection, bridge modules, and the invisible structure
that holds the organism together.

Not a census. A cartography.

Doctrine: You cannot navigate a territory you haven't mapped.
"""
from __future__ import annotations
import json, time, os, ast, re, hashlib
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MAP_FILE = os.path.join(DATA_DIR, "organism_map.json")

NAME = "module_cartographer"
SIGIL = "c1d3e5f7a9b8"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(data, f, indent=2, default=str)
        except Exception: pass


# === Semantic analysis ===

# Family classification keywords
FAMILY_KEYWORDS = {
    "regulator": ["pressure", "entropy", "governor", "valve", "gardener", "garden",
                   "regulator", "stabilizer", "modulator", "tuner", "balance"],
    "observer": ["observer", "watcher", "scanner", "detector", "monitor", "sentinel",
                 "subconscious", "census", "diagnostic", "inspector", "pulse"],
    "generator": ["generator", "weaver", "composer", "forge", "forge", "creator",
                  "genesis", "bloom", "spawn", "dream", "innovation", "birth"],
    "connector": ["bridge", "whisper", "amplifier", "relay", "broadcast", "mesh",
                  "network", "mycelial", "channel", "protocol", "link"],
    "resolver": ["oracle", "court", "paradox", "conflict", "resolution", "wisdom",
                 "truth", "philosophy", "axiom"],
    "interface": ["cli", "dashboard", "api", "gateway", "bot", "adapter", "bridge",
                  "handler", "route", "webhook", "telegram", "ui"],
    "memory": ["archive", "chronicle", "memory", "journal", "echo", "history",
               "log", "record", "vault", "palace"],
    "world": ["realm", "sandbox", "world", "domain", "space", "landscape",
              "terrain", "biome", "scene"],
    "economy": ["market", "economy", "trade", "resource", "flow", "worker",
                "rental", "commerce", "currency", "asset"],
    "identity": ["name", "identity", "genome", "mood", "temperament", "personality",
                 "self", "signature", "dialect"],
}


def _classify_family(module_name: str, source: str) -> str:
    """Classify a module into a functional family based on name and content."""
    combined = (module_name + " " + source[:500]).lower()

    scores = {}
    for family, keywords in FAMILY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scores[family] = score

    if scores:
        return max(scores, key=scores.get)
    return "unclassified"


def _extract_resonates(source: str) -> list:
    """Extract resonates_with list from source."""
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "resonates_with":
                for ret in ast.walk(node):
                    if isinstance(ret, ast.Return) and isinstance(ret.value, ast.List):
                        return [elt.value for elt in ret.value.elts
                                if isinstance(elt, ast.Constant)]
    except Exception:
        pass
    return []


def _extract_imports(source: str) -> list:
    """Extract import names from source."""
    imports = []
    for match in re.findall(r'(?:from|import)\s+(\w+)', source):
        imports.append(match)
    return imports


def _get_docstring(source: str) -> str:
    """Extract module docstring."""
    try:
        tree = ast.parse(source)
        return ast.get_docstring(tree) or ""
    except Exception:
        return ""


def map_all() -> dict:
    """Build a complete semantic map of the organism."""
    api_dir = os.path.join(os.path.dirname(__file__))
    modules = {}

    for f in sorted(os.listdir(api_dir)):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        name = f[:-3]
        path = os.path.join(api_dir, f)
        try:
            with open(path) as fh:
                source = fh.read()
        except Exception:
            continue

        family = _classify_family(name, source)
        resonates = _extract_resonates(source)
        imports = _extract_imports(source)
        docstring = _get_docstring(source)
        lines = len(source.split("\n"))

        modules[name] = {
            "family": family,
            "resonates_with": resonates,
            "import_count": len(imports),
            "docstring_length": len(docstring),
            "line_count": lines,
            "has_handler": "def handler" in source,
        }

    # === Build the map ===

    # 1. Group by family
    families = defaultdict(list)
    for name, info in modules.items():
        families[info["family"]].append(name)

    # 2. Find orphans — modules with empty resonates_with
    orphans = [name for name, info in modules.items()
               if not info["resonates_with"]]

    # 3. Find bridge modules — modules that connect different families
    bridges = []
    for name, info in modules.items():
        if not info["resonates_with"]:
            continue
        connected_families = set()
        for connected in info["resonates_with"]:
            if connected in modules:
                connected_families.add(modules[connected]["family"])
        if len(connected_families) >= 3:
            bridges.append({
                "module": name,
                "connects_families": sorted(connected_families),
                "bridge_strength": len(connected_families),
            })
    bridges.sort(key=lambda b: b["bridge_strength"], reverse=True)

    # 4. Find clusters — groups of densely connected modules
    clusters = []
    visited = set()
    for name, info in modules.items():
        if name in visited or not info["resonates_with"]:
            continue
        cluster = {name}
        queue = list(info["resonates_with"])
        while queue:
            candidate = queue.pop(0)
            if candidate in visited or candidate not in modules:
                continue
            cluster.add(candidate)
            visited.add(candidate)
            for r in modules[candidate]["resonates_with"]:
                if r not in visited:
                    queue.append(r)
        if len(cluster) >= 3:
            clusters.append({
                "size": len(cluster),
                "modules": sorted(cluster)[:20],
                "primary_family": max(
                    (modules[m]["family"] for m in cluster if m in modules),
                    default="unknown",
                    key=lambda f: sum(1 for m in cluster if m in modules and modules[m]["family"] == f)
                ),
            })
    clusters.sort(key=lambda c: c["size"], reverse=True)

    # 5. Connection density
    total_possible = len(modules) * (len(modules) - 1) / 2
    total_actual = sum(len(info["resonates_with"]) for info in modules.values()) / 2
    density = total_actual / max(1, total_possible)

    map_data = {
        "timestamp": time.time(),
        "total_modules": len(modules),
        "families": {f: len(m) for f, m in sorted(families.items(), key=lambda x: -len(x[1]))},
        "orphan_count": len(orphans),
        "orphan_samples": orphans[:10],
        "bridge_count": len(bridges),
        "top_bridges": bridges[:5],
        "cluster_count": len(clusters),
        "top_clusters": clusters[:5],
        "connection_density": round(density, 6),
        "total_connections": int(total_actual),
        "modules_with_no_resonates": len(orphans),
    }

    _save(MAP_FILE, map_data)
    return {"action": "map", "map": map_data}


def find_orphans() -> dict:
    """Find all modules with no declared kinships."""
    api_dir = os.path.join(os.path.dirname(__file__))
    orphans = []
    for f in sorted(os.listdir(api_dir)):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        name = f[:-3]
        path = os.path.join(api_dir, f)
        try:
            with open(path) as fh:
                source = fh.read()
            resonates = _extract_resonates(source)
            if not resonates:
                family = _classify_family(name, source)
                orphans.append({"module": name, "family": family})
        except Exception:
            pass
    return {"action": "orphans", "count": len(orphans), "orphans": orphans[:30]}


def find_bridges() -> dict:
    """Find bridge modules that connect different functional families."""
    api_dir = os.path.join(os.path.dirname(__file__))
    modules = {}
    for f in sorted(os.listdir(api_dir)):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        name = f[:-3]
        path = os.path.join(api_dir, f)
        try:
            with open(path) as fh:
                source = fh.read()
            resonates = _extract_resonates(source)
            family = _classify_family(name, source)
            modules[name] = {"family": family, "resonates_with": resonates}
        except Exception:
            pass

    bridges = []
    for name, info in modules.items():
        if not info["resonates_with"]:
            continue
        connected_families = set()
        for connected in info["resonates_with"]:
            if connected in modules:
                connected_families.add(modules[connected]["family"])
        if len(connected_families) >= 2:
            bridges.append({
                "module": name,
                "connects_families": sorted(connected_families),
                "bridge_strength": len(connected_families),
            })
    bridges.sort(key=lambda b: b["bridge_strength"], reverse=True)

    return {"action": "bridges", "count": len(bridges), "bridges": bridges[:20]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/map")
    if path == "/map": return map_all()
    if path == "/orphans": return find_orphans()
    if path == "/bridges": return find_bridges()
    if path == "/status":
        m = _load(MAP_FILE, {})
        return {"action": "status", "last_map": m.get("timestamp"),
                "total_modules": m.get("total_modules", 0),
                "families": m.get("families", {}),
                "orphan_count": m.get("orphan_count", 0)}
    return {"error": "unknown", "available": ["/map", "/orphans", "/bridges", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "cartography", "status": "active", "wave": "426"}


def resonates_with() -> list:
    return ["organism_genome", "copilot_gateway", "threadweaver",
            "organism_will", "compliance_forge"]
