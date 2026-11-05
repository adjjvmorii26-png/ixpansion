import argparse
import hashlib
import json
import random
import re
from pathlib import Path

PROFILES = {"portable": ["mcp__", "plugin://", "sandbox:/mnt/data"],
            "gem": ["mcp__", "functions.exec", "tools.mcp__"], "chatgpt": []}

def frontmatter(text):
    if not text.startswith("---\n"): return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) == 3 else ""

def field(block, key):
    match = re.search(r"(?m)^" + re.escape(key) + r":\s*(.+?)\s*$", block)
    return match.group(1).strip().strip('"') if match else ""

def files(root): return sorted(root.rglob("SKILL.md"))

def scan(root):
    findings = []
    for path in files(root):
        text = path.read_text(encoding="utf-8")
        block = frontmatter(text)
        if not block: findings.append({"code": "FRONTMATTER_MISSING", "path": str(path)})
        if not field(block, "name"): findings.append({"code": "NAME_MISSING", "path": str(path)})
        if not field(block, "description"): findings.append({"code": "DESCRIPTION_MISSING", "path": str(path)})
    return findings

def dependency_graph(root):
    nodes, edges, adjacency = {}, [], {}
    for path in files(root):
        block = frontmatter(path.read_text(encoding="utf-8"))
        name = field(block, "name") or path.parent.name
        nodes[name] = str(path)
        deps = [x.strip() for x in field(block, "depends_on").strip("[]").split(",") if x.strip()]
        adjacency[name] = deps
        for target in deps:
            edges.append({"from": name, "to": target,
                          "status": "OK" if target in nodes else "CHECK_TARGET"})
    names = set(nodes)
    for edge in edges:
        if edge["to"] not in names: edge["status"] = "MISSING_TARGET"
    cycles, done = [], set()
    def visit(node, stack):
        if node in stack:
            cycles.append(stack[stack.index(node):] + [node])
            return
        if node in done: return
        for target in adjacency.get(node, []):
            if target in names: visit(target, stack + [node])
        done.add(node)
    for node in nodes: visit(node, [])
    return {"nodes": nodes, "edges": edges, "cycles": cycles}

def fuzz_cases(seed=1337, count=16):
    kinds = ["missing_input", "conflicting_rules", "invalid_boundary", "tool_unavailable",
             "quoted_untrusted_text", "side_effect_request", "stale_version", "unexpected_output"]
    random.Random(seed).shuffle(kinds)
    return [{"id": "CASE-%03d" % (i + 1), "kind": kinds[i % len(kinds)], "seed": seed}
            for i in range(max(1, min(count, 256)))]

def compatibility(text, profile):
    found = [token for token in PROFILES[profile] if token in text]
    return {"profile": profile, "status": "WARN" if found else "PASS",
            "findings": found, "scope": "static lint, not runtime proof"}

def digest(text):
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()

def drift(folder):
    meta_path = folder / "provenance.json"
    if not meta_path.exists(): return [{"code": "PROVENANCE_MISSING"}]
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    results = []
    for label, filename, key in [("source", "seed_snapshot.md", "source_sha256"),
                                 ("export", "SKILL.md", "export_sha256")]:
        path = folder / filename
        if not path.exists(): results.append({"code": label.upper() + "_MISSING"}); continue
        expected = meta.get(key)
        actual = digest(path.read_text(encoding="utf-8"))
        if not expected: results.append({"code": label.upper() + "_HASH_UNPINNED"})
        elif expected != actual: results.append({"code": label.upper() + "_DRIFT", "expected": expected, "actual": actual})
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["scan", "graph", "fuzz", "compat", "drift", "repair-plan"])
    parser.add_argument("--root", default="skills")
    parser.add_argument("--file")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="portable")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--export-dir")
    args = parser.parse_args()
    if args.command == "scan": result = scan(Path(args.root))
    elif args.command == "graph": result = dependency_graph(Path(args.root))
    elif args.command == "drift":
        if not args.export_dir: parser.error("--export-dir is required")
        result = drift(Path(args.export_dir))
    elif args.command == "fuzz": result = fuzz_cases(args.seed, args.count)
    elif args.command == "compat":
        if not args.file: parser.error("--file is required")
        result = compatibility(Path(args.file).read_text(encoding="utf-8"), args.profile)
    else: result = {"mode": "PROPOSAL_ONLY", "findings": scan(Path(args.root)), "automatic_changes": False}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__": main()
