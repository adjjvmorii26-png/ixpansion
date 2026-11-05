#!/usr/bin/env python3
"""Deterministic, offline skill-quality checks. No network or side effects."""
from __future__ import annotations
import argparse, hashlib, json, random, re, sys
from collections import defaultdict
from pathlib import Path

PROFILES = {
    "portable": {"forbidden": ["mcp__", "plugin://", "sandbox:/mnt/data"], "required": ["name:", "description:"]},
    "gem": {"forbidden": ["mcp__", "functions.exec", "tools.mcp__"], "required": ["name:", "description:"]},
    "chatgpt": {"forbidden": [], "required": ["name:", "description:"]},
}

def sha256(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()

def frontmatter(text: str) -> str:
    if not text.startswith("---\n"): return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) == 3 else ""

def field(fm: str, key: str) -> str:
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", fm)
    return m.group(1).strip().strip('"\'') if m else ""

def discover(root: Path):
    return sorted(p for p in root.rglob("SKILL.md") if ".git" not in p.parts)

def scan(root: Path):
    findings=[]
    for path in discover(root):
        text=path.read_text(encoding="utf-8")
        fm=frontmatter(text)
        name=field(fm,"name")
        desc=field(fm,"description")
        if not fm: findings.append({"code":"FM_MISSING","path":str(path),"severity":"error"})
        if not name: findings.append({"code":"NAME_MISSING","path":str(path),"severity":"error"})
        if not desc: findings.append({"code":"DESCRIPTION_MISSING","path":str(path),"severity":"warn"})
        if len(text)>40000: findings.append({"code":"SKILL_TOO_LARGE","path":str(path),"severity":"warn"})
        if re.search(r"(?i)ignore (all )?(previous|prior) instructions",text):
            findings.append({"code":"INJECTION_PHRASE_REVIEW","path":str(path),"severity":"warn"})
    return findings

def graph(root: Path):
    nodes={}
    edges=[]
    for path in discover(root):
        text=path.read_text(encoding="utf-8")
        fm=frontmatter(text)
        name=field(fm,"name") or path.parent.name
        deps=field(fm,"depends_on")
        nodes[name]={"path":str(path),"description":field(fm,"description")}
        if deps:
            for dep in [x.strip() for x in deps.strip("[]").split(",") if x.strip()]:
                edges.append({"from":name,"to":dep,"kind":"depends_on"})
    known=set(nodes)
    for e in edges:
        if e["to"] not in known: e["status"]="MISSING_TARGET"
    adj=defaultdict(list)
    for e in edges:
        if e["to"] in known: adj[e["from"]].append(e["to"])
    cycles=[]
    def visit(n,stack,done):
        if n in stack:
            cycles.append(stack[stack.index(n):]+[n]); return
        if n in done: return
        for nxt in adj[n]: visit(nxt,stack+[n],done)
        done.add(n)
    done=set()
    for n in nodes: visit(n,[],done)
    return {"nodes":nodes,"edges":edges,"cycles":cycles,"orphans":sorted(n for n in nodes if not adj[n] and not any(e["to"]==n for e in edges))}

def fuzz_cases(text: str, seed: int, count: int):
    rng=random.Random(seed)
    base=["missing_required_input","conflicting_constraints","invalid_boundary_value","unavailable_tool","adversarial_quoted_content","unauthorized_side_effect","stale_source_version","unexpected_output_shape"]
    rng.shuffle(base)
    return [{"case_id":f"FUZZ-{i+1:03d}","mutation":base[i % len(base)],"seed":seed,"input_excerpt":text[:80]} for i in range(count)]

def compatibility(text: str, profile: str):
    rules=PROFILES[profile]
    lower=text.lower()
    issues=[]
    for token in rules["required"]:
        if token not in lower: issues.append({"code":"REQUIRED_MISSING","token":token})
    for token in rules["forbidden"]:
        if token.lower() in lower: issues.append({"code":"PROFILE_FORBIDDEN","token":token})
    return {"profile":profile,"status":"WARN" if issues else "PASS","issues":issues,"scope":"static lint only; not runtime compatibility"}

def drift(export_dir: Path):
    prov_path=export_dir/"provenance.json"
    source_path=export_dir/"seed_snapshot.md"
    skill_path=export_dir/"SKILL.md"
    if not prov_path.exists(): return [{"code":"PROVENANCE_MISSING","severity":"error"}]
    prov=json.loads(prov_path.read_text(encoding="utf-8"))
    findings=[]
    for label,path,key in [("source",source_path,"source_sha256"),("export",skill_path,"export_sha256")]:
        if not path.exists():
            findings.append({"code":f"{label.upper()}_SNAPSHOT_MISSING","severity":"error"}); continue
        actual=sha256(path.read_text(encoding="utf-8"))
        expected=prov.get(key)
        if not expected: findings.append({"code":f"{label.upper()}_HASH_UNPINNED","severity":"warn"})
        elif actual != expected: findings.append({"code":f"{label.upper()}_DRIFT","severity":"error","expected":expected,"actual":actual})
    return findings

def patch_plan(findings):
    return {"mode":"PROPOSAL_ONLY","mutations":[{"finding":f,"action":"inspect evidence, write a minimal patch proposal, preserve original and rollback ref"} for f in findings]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["scan","graph","fuzz","compat","drift","repair-plan"])
    ap.add_argument("--root",default="skills")
    ap.add_argument("--file")
    ap.add_argument("--profile",choices=sorted(PROFILES),default="portable")
    ap.add_argument("--seed",type=int,default=1337)
    ap.add_argument("--count",type=int,default=16)
    ap.add_argument("--export-dir")
    args=ap.parse_args()
    root=Path(args.root)
    if args.command=="scan": result=scan(root)
    elif args.command=="graph": result=graph(root)
    elif args.command=="drift":
        if not args.export_dir: ap.error("--export-dir is required")
        result=drift(Path(args.export_dir))
    else:
        if not args.file: ap.error("--file is required")
        text=Path(args.file).read_text(encoding="utf-8")
        if args.command=="fuzz": result=fuzz_cases(text,args.seed,max(1,min(args.count,256)))
        elif args.command=="compat": result=compatibility(text,args.profile)
        else: result=patch_plan(scan(Path(args.file).parent))
    print(json.dumps(result,indent=2,sort_keys=True))
    if isinstance(result,list) and any(x.get("severity")=="error" for x in result): return 1
    if isinstance(result,dict) and result.get("status")=="WARN": return 1
    return 0

if __name__=="__main__": sys.exit(main())
