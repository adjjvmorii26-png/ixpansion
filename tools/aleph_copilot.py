#!/usr/bin/env python3
"""
aleph_copilot — Axiium Protocol's Local GitHub Copilot
A local coding companion that knows the organism's architecture,
suggests modules, reviews code, fixes compliance, and generates
context-aware module templates.

Not a remote API. A local brain that lives in the repo.

Usage:
    python3 tools/aleph_copilot.py suggest [topic]
    python3 tools/aleph_copilot.py review <file.py>
    python3 tools/aleph_copilot.py fix [--dry-run]
    python3 tools/aleph_copilot.py template <name> [family]
    python3 tools/aleph_copilot.py map
    python3 tools/aleph_copilot.py status
    python3 tools/aleph_copilot.py wizard
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

# === Config ===
API_DIR = os.path.join(os.path.dirname(__file__), "..", "api")
TOOLS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(REPO_ROOT, "data")

# === Colored output ===
class C:
    GOLD = "\033[38;5;220m"
    VIOLET = "\033[38;5;141m"
    GREEN = "\033[38;5;114m"
    RED = "\033[38;5;203m"
    BLUE = "\033[38;5;117m"
    DIM = "\033[38;5;240m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def p(color, text):
    print(f"{color}{text}{C.RESET}")

def header(text):
    p(C.BOLD + C.GOLD, f"\n{'='*60}")
    p(C.BOLD + C.GOLD, f"  {text}")
    p(C.BOLD + C.GOLD, f"{'='*60}\n")

# === Module analysis ===
def get_all_modules():
    modules = {}
    for f in sorted(os.listdir(API_DIR)):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        name = f[:-3]
        path = os.path.join(API_DIR, f)
        try:
            with open(path) as fh:
                source = fh.read()
            tree = ast.parse(source)
            funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            docstring = ast.get_docstring(tree) or ""
            resonates = extract_resonates(tree)
            family = classify_family(name, source)
            modules[name] = {
                "family": family,
                "functions": funcs,
                "has_handler": "handler" in funcs,
                "has_vitals": "coherence_vitals" in funcs,
                "has_resonates": "resonates_with" in funcs,
                "docstring": docstring[:200],
                "resonates_with": resonates,
                "lines": len(source.split("\n")),
                "path": path,
            }
        except Exception:
            pass
    return modules

def extract_resonates(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "resonates_with":
            for ret in ast.walk(node):
                if isinstance(ret, ast.Return) and isinstance(ret.value, ast.List):
                    return [e.value for e in ret.value.elts if isinstance(e, ast.Constant)]
    return []

FAMILY_KW = {
    "regulator": ["pressure", "entropy", "valve", "gardener", "garden", "balance"],
    "observer": ["observer", "watcher", "scanner", "detector", "monitor", "pulse"],
    "generator": ["weaver", "forge", "dream", "bloom", "composer", "innovation"],
    "connector": ["bridge", "whisper", "amplifier", "relay", "mesh", "network"],
    "resolver": ["oracle", "court", "paradox", "wisdom", "truth"],
    "interface": ["cli", "dashboard", "api", "gateway", "bot", "handler"],
    "memory": ["archive", "chronicle", "memory", "journal", "echo", "history"],
    "world": ["realm", "sandbox", "world", "domain", "space"],
    "economy": ["market", "economy", "trade", "resource", "worker"],
    "identity": ["name", "identity", "genome", "mood", "temperament"],
}

def classify_family(name, source):
    combined = (name + " " + source[:500]).lower()
    scores = {}
    for fam, kws in FAMILY_KW.items():
        s = sum(1 for kw in kws if kw in combined)
        if s > 0:
            scores[fam] = s
    return max(scores, key=scores.get) if scores else "unclassified"

# === Commands ===

def cmd_suggest(topic=None):
    header("💡 Module Suggestion")
    modules = get_all_modules()

    # Count families
    families = Counter(m["family"] for m in modules.values())
    orphans = [n for n, m in modules.items() if not m["resonates_with"]]

    p(C.DIM, f"Organism has {len(modules)} modules across {len(families)} families\n")

    if topic:
        p(C.VIOLET, f"Suggesting modules related to: {topic}\n")
        # Find related existing modules
        related = [(n, m) for n, m in modules.items()
                   if topic.lower() in n.lower() or topic.lower() in m["docstring"].lower()]
        if related:
            p(C.BLUE, "Existing related modules:")
            for n, m in related[:5]:
                p(C.GREEN, f"  {n} ({m['family']}) — {m['docstring'][:80]}")
            p(C.DIM, "")

    # Suggest underserved families
    min_family = families.most_common()[-1] if families else ("unknown", 0)
    p(C.VIOLET, f"Underserved family: {min_family[0]} ({min_family[1]} modules)")

    # Suggest orphan adoption
    if orphans:
        p(C.VIOLET, f"Orphans needing kinships: {len(orphans)}")
        for o in orphans[:3]:
            p(C.DIM, f"  → {o}")

    # Generate suggestions
    import random
    adjectives = ["resonant", "spectral", "fractal", "mycelial", "luminous",
                  "temporal", "void-touched", "root-veined", "dream-woven"]
    nouns = ["observer", "weaver", "gardener", "oracle", "forge",
             "messenger", "cathedral", "loom", "threshold", "compass"]

    suggestions = []
    for _ in range(3):
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        name = f"{adj}_{noun}"
        if name not in modules:
            # Find a family that needs more modules
            target_family = min_family[0]
            suggestions.append({
                "name": name,
                "family": target_family,
                "purpose": f"fills the {target_family} family gap",
            })

    p(C.GOLD, "\nSuggested modules:")
    for s in suggestions:
        p(C.GREEN, f"  {s['name']}.py — {s['family']}: {s['purpose']}")
        p(C.DIM, f"    → python3 tools/aleph_copilot.py template {s['name']} {s['family']}")

    return suggestions


def cmd_review(filepath):
    header(f"🔍 Reviewing: {filepath}")

    if not os.path.exists(filepath):
        p(C.RED, f"File not found: {filepath}")
        return

    with open(filepath) as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        p(C.RED, f"SYNTAX ERROR: {e}")
        return

    name = os.path.basename(filepath).replace(".py", "")
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    required = {"handler", "coherence_vitals", "resonates_with"}
    missing = required - funcs

    issues = []
    warnings = []

    # Contract check
    if missing:
        issues.append(f"Missing contract methods: {missing}")
    else:
        p(C.GREEN, "✓ All contract methods present")

    # f-string check
    if 'f"' in source and "\\n" in source:
        warnings.append("f-string with literal newline — may break heredoc patching")

    # import os inside functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        if alias.name == "os":
                            issues.append(f"import os inside {node.name}() shadows module-level os")

    # Docstring check
    docstring = ast.get_docstring(tree)
    if not docstring:
        warnings.append("No module docstring")
    elif len(docstring) < 20:
        warnings.append(f"Docstring very short ({len(docstring)} chars)")

    # Line count
    lines = len(source.split("\n"))
    if lines > 500:
        warnings.append(f"Large module ({lines} lines) — consider splitting")

    # Resonates check
    resonates = extract_resonates(tree)
    if not resonates:
        warnings.append("No kinships declared (empty resonates_with)")

    # Print results
    if issues:
        p(C.RED, "\nIssues:")
        for i in issues:
            p(C.RED, f"  ✗ {i}")

    if warnings:
        p(C.YELLOW if hasattr(C, 'YELLOW') else C.GOLD, "\nWarnings:")
        for w in warnings:
            p(C.GOLD, f"  ⚠ {w}")

    if not issues and not warnings:
        p(C.GREEN, "\n✓ Module looks clean")

    # Suggest fixes
    if missing:
        p(C.VIOLET, "\nSuggested fix:")
        p(C.DIM, f"  python3 tools/aleph_copilot.py fix {filepath}")

    return {"issues": issues, "warnings": warnings, "missing": list(missing)}


def cmd_fix(dry_run=False):
    header("🔧 Compliance Forge")
    modules = get_all_modules()

    fixed = 0
    for name, info in modules.items():
        if info["has_handler"] and info["has_vitals"] and info["has_resonates"]:
            continue

        path = info["path"]
        with open(path) as f:
            source = f.read()

        missing = []
        if not info["has_vitals"]:
            missing.append("coherence_vitals")
        if not info["has_resonates"]:
            missing.append("resonates_with")
        if not info["has_handler"]:
            missing.append("handler")

        if dry_run:
            p(C.GOLD, f"  Would patch {name}: missing {missing}")
        else:
            patches = []
            if "coherence_vitals" in missing:
                patches.append(f'\ndef coherence_vitals() -> dict:\n    return {{"layer": "{info["family"]}", "status": "active", "module": "{name}"}}\n')
            if "resonates_with" in missing:
                patches.append(f'\ndef resonates_with() -> list:\n    return ["organism_genome", "threadweaver"]\n')
            if "handler" in missing:
                patches.append(f'\ndef handler(payload=None, context=None):\n    payload = payload or {{}}\n    return {{"action": "status", "module": "{name}", "status": "active"}}\n')

            with open(path, "a") as f:
                f.write("\n# --- aleph_copilot patch ---\n")
                for p_text in patches:
                    f.write(p_text)
            p(C.GREEN, f"  ✓ Patched {name}: added {missing}")

        fixed += 1

    action = "would patch" if dry_run else "patched"
    p(C.BOLD + C.GOLD, f"\n{action} {fixed} modules")


def cmd_template(name, family="unclassified"):
    header(f"📝 Generating template: {name}")

    sigil = hashlib.sha256(name.encode()).hexdigest()[:12]
    template = (
        '''"""
%s â Organism module
Generated by aleph_copilot
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


def coherence_vitals() -> dict:
    return {"layer": "%s", "status": "active", "module": NAME}


def resonates_with() -> list:
    return ["organism_genome", "threadweaver"]
''' % (name, name, sigil, family)
    )

    outpath = os.path.join(API_DIR, f"{name}.py")
    if os.path.exists(outpath):
        p(C.RED, f"File already exists: {outpath}")
        return

    with open(outpath, "w") as f:
        f.write(template)
    p(C.GREEN, f"✓ Created {outpath}")
    p(C.DIM, f"  → Add route: {{\"src\": \"/api/{name}\", \"dest\": \"/api/index.py\"}}")
    p(C.DIM, f"  → Compile: python3 -m py_compile {outpath}")


def cmd_map():
    header("🗺 Organism Map")
    modules = get_all_modules()
    families = Counter(m["family"] for m in modules.values())
    orphans = [n for n, m in modules.items() if not m["resonates_with"]]
    total_connections = sum(len(m["resonates_with"]) for m in modules.values())

    p(C.BOLD + C.GOLD, f"Total modules: {len(modules)}")
    p(C.BOLD + C.GOLD, f"Families:")
    for fam, count in families.most_common():
        bar = "█" * min(count, 40)
        p(C.VIOLET, f"  {fam:15s} {count:4d} {C.DIM}{bar}")

    p(C.BOLD + C.GOLD, f"\nOrphans: {len(orphans)}")
    for o in orphans[:5]:
        p(C.DIM, f"  → {o}")

    p(C.BOLD + C.GOLD, f"\nTotal connections: {total_connections}")
    p(C.BOLD + C.GOLD, f"Density: {total_connections / max(1, len(modules) * (len(modules)-1) / 2):.6f}")


def cmd_status():
    header("📊 Axiium Protocol Status")
    modules = get_all_modules()
    families = Counter(m["family"] for m in modules.values())
    compliant = sum(1 for m in modules.values()
                    if m["has_handler"] and m["has_vitals"] and m["has_resonates"])

    p(C.BOLD + C.GOLD, f"Name: Axiium Protocol")
    p(C.BOLD + C.GOLD, f"Modules: {len(modules)}")
    p(C.BOLD + C.GOLD, f"Compliant: {compliant}/{len(modules)} ({compliant*100//len(modules)}%)")
    p(C.BOLD + C.GOLD, f"Families: {len(families)}")
    p(C.BOLD + C.GOLD, f"Top family: {families.most_common(1)[0][0]} ({families.most_common(1)[0][1]})")

    # Read genome if available
    genome_path = os.path.join(DATA_DIR, "organism_name.json")
    if os.path.exists(genome_path):
        with open(genome_path) as f:
            name_data = json.load(f)
        current = name_data.get("current", {})
        p(C.BOLD + C.GOLD, f"Self-chosen name: {current.get('name', '?')}")
        p(C.DIM, f"  {current.get('declaration', '')[:80]}")


def cmd_wizard():
    header("🧙 Axiium Copilot Wizard")
    p(C.VIOLET, "What would you like to do?\n")
    p(C.GREEN, "  1. Suggest a new module")
    p(C.GREEN, "  2. Review a module file")
    p(C.GREEN, "  3. Fix compliance issues")
    p(C.GREEN, "  4. Generate a module template")
    p(C.GREEN, "  5. View organism map")
    p(C.GREEN, "  6. Check organism status")
    p(C.GREEN, "  7. Auto-fix all modules")
    p(C.DIM, "\n  Usage: python3 tools/aleph_copilot.py <command> [args]\n")


def main():
    if len(sys.argv) < 2:
        cmd_wizard()
        return

    command = sys.argv[1]

    if command == "suggest":
        topic = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_suggest(topic)
    elif command == "review":
        if len(sys.argv) < 3:
            p(C.RED, "Usage: aleph_copilot review <file.py>")
            return
        cmd_review(sys.argv[2])
    elif command == "fix":
        dry_run = "--dry-run" in sys.argv
        cmd_fix(dry_run)
    elif command == "template":
        if len(sys.argv) < 3:
            p(C.RED, "Usage: aleph_copilot template <name> [family]")
            return
        name = sys.argv[2]
        family = sys.argv[3] if len(sys.argv) > 3 else "unclassified"
        cmd_template(name, family)
    elif command == "map":
        cmd_map()
    elif command == "status":
        cmd_status()
    elif command == "wizard":
        cmd_wizard()
    else:
        p(C.RED, f"Unknown command: {command}")
        cmd_wizard()


if __name__ == "__main__":
    main()
