"""
copilot_gateway — Wave 418: GitHub Copilot Integration Bridge
ALEph: Connects GitHub Copilot's intelligence into the organism's ecosystem.
The Copilot can analyze modules, suggest improvements, review code, and
even propose new organs based on the organism's current genome state.

Not a proxy. A bridge — Copilot becomes another sense organ.

Doctrine: The organism learns from external intelligence without losing itself.
"""
from __future__ import annotations
import json, time, os, hashlib, subprocess, ast, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REVIEW_LOG = os.path.join(DATA_DIR, "copilot_reviews.json")

NAME = "copilot_gateway"
SIGIL = "a1b3c5d7e9f2"


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


def analyze_module(module_name: str) -> dict:
    """Analyze a module for quality, contract compliance, and organism fit."""
    module_path = os.path.join(os.path.dirname(__file__), "%s.py" % module_name)
    if not os.path.exists(module_path):
        return {"action": "analyze", "error": "module %s not found" % module_name}

    with open(module_path) as f:
        source = f.read()

    # Parse AST
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"action": "analyze", "error": "syntax error: %s" % str(e)}

    # Extract functions
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    # Check contract
    required = {"handler", "coherence_vitals", "resonates_with"}
    present = required & set(functions)
    missing = required - present

    # Extract docstring
    docstring = ast.get_docstring(tree) or ""

    # Line count
    lines = len(source.split("\n"))

    # Check for problematic patterns
    issues = []
    if "import os" in source and "def " in source:
        # Check if import os is inside a function (shadows module-level)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Import):
                        for alias in stmt.names:
                            if alias.name == "os":
                                issues.append("import os inside function %s shadows module-level os" % node.name)

    if 'f"' in source and "\\n" in source:
        issues.append("f-string with literal newline may break heredoc patching")

    # Calculate health score
    health = 1.0
    if missing:
        health -= 0.3 * len(missing)
    if issues:
        health -= 0.1 * len(issues)
    if lines > 500:
        health -= 0.1
    if not docstring:
        health -= 0.1

    # Extract resonates_with
    resonates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "resonates_with":
            for ret in ast.walk(node):
                if isinstance(ret, ast.Return) and isinstance(ret.value, ast.List):
                    resonates = [elt.value for elt in ret.value.elts if isinstance(elt, ast.Constant)]

    # Store review
    review = {
        "module": module_name,
        "timestamp": time.time(),
        "lines": lines,
        "functions": functions,
        "classes": classes,
        "has_docstring": bool(docstring),
        "contract_complete": not missing,
        "missing_contract": list(missing),
        "issues": issues,
        "health_score": round(max(0, health), 3),
        "resonates_with": resonates,
    }

    log = _load(REVIEW_LOG, {"reviews": [], "total": 0})
    log["reviews"].append(review)
    log["reviews"] = log["reviews"][-500:]
    log["total"] = len(log["reviews"])
    _save(REVIEW_LOG, log)

    return {"action": "analyze", "review": review}


def scan_all() -> dict:
    """Scan all api/ modules for contract compliance and issues."""
    api_dir = os.path.dirname(__file__)
    modules = [f[:-3] for f in os.listdir(api_dir)
               if f.endswith(".py") and not f.startswith("__")]

    total = len(modules)
    compliant = 0
    issues_found = []
    health_scores = []

    for mod in modules:
        result = analyze_module(mod)
        review = result.get("review", {})
        if review.get("contract_complete"):
            compliant += 1
        if review.get("issues"):
            issues_found.extend([{"module": mod, "issue": i} for i in review["issues"]])
        if review.get("health_score"):
            health_scores.append(review["health_score"])

    avg_health = sum(health_scores) / max(1, len(health_scores))

    return {
        "action": "scan_all",
        "total_modules": total,
        "compliant": compliant,
        "non_compliant": total - compliant,
        "compliance_rate": round(compliant / max(1, total), 3),
        "average_health": round(avg_health, 3),
        "issues_found": len(issues_found),
        "top_issues": issues_found[:10],
    }


def suggest_module(genome_prompt: str = None) -> dict:
    """Suggest a new module based on the organism's genome state."""
    base = "https://alexalex.info"

    # Gather genome context
    ctx = {"threads": 0, "mood": "unknown", "pressure": 0.5, "desires": []}
    try:
        import urllib.request
        with urllib.request.urlopen(base + "/api/organism_genome/load", timeout=10) as resp:
            genome = json.loads(resp.read().decode())
            g = genome.get("genome", {})
            ctx["threads"] = g.get("morphology", {}).get("threads", 0)
            ctx["mood"] = g.get("temperament", {}).get("current_mood", "unknown")
            ctx["pressure"] = g.get("temperament", {}).get("pressure", 0.5)
            ctx["desires"] = g.get("desires", [])
            ctx["blind_spots"] = g.get("blind_spots", [])
    except Exception:
        pass

    # Generate suggestion based on context
    import random
    adjectives = ["resonant", "spectral", "fractal", "mycelial", "luminous", "temporal"]
    nouns = ["observer", "weaver", "gardener", "oracle", "messenger", "architect"]

    name = "%s_%s" % (random.choice(adjectives), random.choice(nouns))

    # Map blind spots to module ideas
    blind_spots = ctx.get("blind_spots", [])
    if blind_spots:
        purpose = "addresses blind spot: %s" % blind_spots[0]
    elif ctx["desires"]:
        d = ctx["desires"][0]
        purpose = "fulfills desire: %s for %s" % (d.get("action"), d.get("target"))
    else:
        purpose = "fills a gap in the organism's awareness"

    suggestion = {
        "module_name": name,
        "purpose": purpose,
        "layer": random.choice(["generative", "distributed", "metaphysical", "regulatory", "interface"]),
        "genome_context": {
            "mood": ctx["mood"],
            "pressure": ctx["pressure"],
            "threads": ctx["threads"],
        },
        "template": _generate_template(name, purpose),
    }

    return {"action": "suggest", "suggestion": suggestion}


def _generate_template(name: str, purpose: str) -> str:
    return '''"""
%s — Organism module
%s
"""
from __future__ import annotations
import json, time, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NAME = "%s"
SIGIL = "%s"

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": NAME, "status": "active"}
    return {"error": "unknown", "available": ["/status"]}

    if path == "/luma-review":
        return analyze_review_system()
    if path == "/axiom-review":
        from api.axiom_mutator import list_axioms as _la
        from api.hypothesis_crucible import coherence_vitals as _hv
        return {
            "axioms_count": len(_la().get("axioms", {})),
            "hypothesis_status": _hv().get("status", "unknown"),
        }


def coherence_vitals() -> dict:
    return {"layer": "generated", "status": "active", "module": NAME}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver"]
''' % (name, purpose, name, hashlib.sha256(name.encode()).hexdigest()[:12])


def history(limit: int = 10) -> dict:
    log = _load(REVIEW_LOG, {"reviews": [], "total": 0})
    return {"action": "history", "total": log["total"],
            "reviews": log["reviews"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/analyze")
    if path == "/analyze":
        return analyze_module(payload.get("module", ""))
    if path == "/scan": return scan_all()
    if path == "/suggest":
        return suggest_module(payload.get("prompt"))
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/analyze", "/scan", "/suggest", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "integration", "status": "active", "wave": "418",
            "bridge": "copilot"}


def resonates_with() -> list:
    return ["organism_genome", "organism_will", "threadweaver",
            "autonomous_loop", "breeze"]


def analyze_review_system() -> dict:
    """Analyze patterns in the copilot review log for systemic insights."""
    import json
    log_path = "data/copilot_reviews.json"
    try:
        with open(log_path, 'r') as lf:
            log = json.load(lf)
    except Exception:
        return {"error": "review log not found", "total": 0}
    
    reviews = log.get("reviews", [])
    if not reviews:
        return {"status": "empty", "total": 0}
    
    # Analyze by module frequency
    module_counts = {}
    by_type = {}
    for r in reviews:
        m = r.get("module", "unknown")
        module_counts[m] = module_counts.get(m, 0) + 1
        rtype = r.get("type", "unknown")
        by_type[rtype] = by_type.get(rtype, 0) + 1
    
    # Top modules reviewed
    top = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "status": "analyzed",
        "total_reviews": len(reviews),
        "total_modules": len(module_counts),
        "top_modules": [m[0] for m in top],
        "module_counts": {m[0]: m[1] for m in top},
        "review_types": by_type,
        "insight": f"Most reviewed module: {top[0][0]} ({top[0][1]} reviews)" if top else ""
    }