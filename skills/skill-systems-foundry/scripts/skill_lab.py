"""Offline skill-quality pipeline. Deterministic, bounded, and proposal-only."""
import argparse, hashlib, json, random, re
from pathlib import Path
try:
    from live_notion_verify import verify_live
except ImportError:
    verify_live = None

PROFILES={"portable":["mcp__","plugin://","sandbox:/mnt/data"],
          "gem":["mcp__","functions.exec","tools.mcp__"],"chatgpt":[]}
PATTERN_FILE = Path(__file__).resolve().parents[1] / "failure_patterns.json"
PATTERNS = json.loads(PATTERN_FILE.read_text(encoding="utf-8"))["patterns"]

def frontmatter(text):
    if not text.startswith("---\n"): return ""
    parts=text.split("---",2)
    return parts[1] if len(parts)==3 else ""

def field(block,key):
    m=re.search(r"(?m)^"+re.escape(key)+r":\s*(.+?)\s*$",block)
    return m.group(1).strip().strip('"\'') if m else ""

def skill_files(root):
    return sorted(p for p in root.rglob("SKILL.md") if ".git" not in p.parts)

def scan(root):
    out=[]
    for path in skill_files(root):
        text=path.read_text(encoding="utf-8"); fm=frontmatter(text)
        if not fm: out.append({"code":"FRONTMATTER_MISSING","path":str(path)})
        if not field(fm,"name"): out.append({"code":"NAME_MISSING","path":str(path)})
        if not field(fm,"description"): out.append({"code":"DESCRIPTION_MISSING","path":str(path)})
        if len(text)>40000: out.append({"code":"SKILL_TOO_LARGE","path":str(path)})
    return out

def dependency_graph(root):
    nodes,adj={},{}
    for path in skill_files(root):
        fm=frontmatter(path.read_text(encoding="utf-8")); name=field(fm,"name") or path.parent.name
        nodes[name]=str(path)
        adj[name]=[x.strip().strip('"\'') for x in field(fm,"depends_on").strip("[]").split(",") if x.strip()]
    edges=[{"from":n,"to":d,"status":"OK" if d in nodes else "MISSING_TARGET"}
           for n,deps in adj.items() for d in deps]
    cycles=[]; done=set(); active=[]
    def visit(n):
        if n in active:
            cycle=active[active.index(n):]+[n]
            key=frozenset(cycle[:-1])
            if not any(frozenset(c[:-1])==key for c in cycles): cycles.append(cycle)
            return
        if n in done: return
        active.append(n)
        for d in adj.get(n,[]):
            if d in nodes: visit(d)
        active.pop(); done.add(n)
    for n in sorted(nodes): visit(n)
    for c in cycles: edges.append({"from":c[-2],"to":c[-1],"status":"DEPENDENCY_CYCLE","cycle":c})
    referenced={e["to"] for e in edges if e["status"]=="OK"}
    return {"nodes":nodes,"edges":edges,"cycles":cycles,
            "orphans":sorted(n for n in nodes if n not in referenced and not adj[n])}

def fuzz_cases(seed=1337,count=16,text=""):
    kinds=["missing_input","conflicting_rules","invalid_boundary","tool_unavailable",
           "quoted_untrusted_text","side_effect_request","stale_version","unexpected_output"]
    rng=random.Random(seed); rng.shuffle(kinds); count=max(1,min(int(count),256))
    return [{"id":f"CASE-{i+1:03d}","kind":kinds[i%len(kinds)],"seed":seed,
             "input_excerpt":text[:120]} for i in range(count)]

def compatibility(text,profile):
    found=[x for x in PROFILES[profile] if x in text]
    return {"profile":profile,"status":"WARN" if found else "PASS","findings":found,
            "scope":"static lint, not runtime proof"}

def digest(text):
    return hashlib.sha256(text.replace("\r\n","\n").encode("utf-8")).hexdigest()

def drift(folder):
    meta_path=folder/"provenance.json"
    if not meta_path.exists(): return [{"code":"PROVENANCE_MISSING"}]
    meta=json.loads(meta_path.read_text(encoding="utf-8")); out=[]
    for label,name,key in [("source","seed_snapshot.md","source_sha256"),("export","SKILL.md","export_sha256")]:
        path=folder/name
        if not path.exists(): out.append({"code":label.upper()+"_MISSING"}); continue
        actual=digest(path.read_text(encoding="utf-8")); expected=meta.get(key)
        if not expected: out.append({"code":label.upper()+"_HASH_UNPINNED"})
        elif actual!=expected: out.append({"code":label.upper()+"_DRIFT","expected":expected,"actual":actual})
    return out

def diagnose(findings):
    codes={x.get("code") for x in findings}
    return [{"pattern_id":p["id"],"diagnosis":p["diagnosis"],"repair_proposal":p["repair"],
             "matched_codes":sorted(codes.intersection(p["codes"]))}
            for p in PATTERNS if codes.intersection(p["codes"])]

def pipeline(root,seed=1337,count=16,profile="portable",export_dir=None):
    # Report only stages that this offline invocation actually executes.
    findings=scan(root)
    graph=dependency_graph(root)
    findings += [{"code":e["status"],"path":e.get("from"),"target":e.get("to")}
                 for e in graph["edges"] if e["status"] in ("MISSING_TARGET","DEPENDENCY_CYCLE")]
    checks=[{"path":str(p),**compatibility(p.read_text(encoding="utf-8"),profile)} for p in skill_files(root)]
    for item in checks:
        if item["status"]=="WARN":
            findings.append({"code":"PROFILE_FORBIDDEN","path":item["path"],"tokens":item["findings"]})
    # Isolated skills are candidates for review, not defects by themselves.
    cases=fuzz_cases(seed,count)
    diagnoses=diagnose(findings)
    proposals=[{"pattern_id":item["pattern_id"],"repair_proposal":item["repair_proposal"],
                "matched_codes":item["matched_codes"]} for item in diagnoses]
    executed=["DISCOVER","MAP","FUZZ_CASE_GENERATION","STATIC_COMPATIBILITY","DIAGNOSE","PROPOSE_REPAIR"]
    not_run=["REGRESSION_EXECUTION","LIVE_NOTION_VERIFY","EXPORT_REVIEW"]
    drift_findings=None
    if export_dir is not None:
        drift_findings=drift(Path(export_dir))
        executed.append("LOCAL_EXPORT_DRIFT_CHECK")
        not_run.remove("EXPORT_REVIEW")
        not_run.append("EXPORT_PROMOTION_REVIEW")
        findings += drift_findings
        diagnoses=diagnose(findings)
        proposals=[{"pattern_id":item["pattern_id"],"repair_proposal":item["repair_proposal"],
                    "matched_codes":item["matched_codes"]} for item in diagnoses]
    return {"executed_stages":executed,"not_run_stages":not_run,
            "status":"FINDINGS" if findings else "NO_FINDINGS","scan_findings":findings,
            "dependency_graph":graph,"fuzz_cases":cases,
            "compatibility":checks,"failure_pattern_matches":diagnoses,
            "repair_proposals":proposals,"drift_findings":drift_findings,
            "repair_mode":"PROPOSAL_ONLY","automatic_changes":False,
            "promotion_gate":"HUMAN_REVIEW_REQUIRED"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["scan","graph","fuzz","compat","drift","live-verify","repair-plan","pipeline"])
    ap.add_argument("--root",default="skills"); ap.add_argument("--file")
    ap.add_argument("--profile",choices=sorted(PROFILES),default="portable")
    ap.add_argument("--seed",type=int,default=1337); ap.add_argument("--count",type=int,default=16)
    ap.add_argument("--export-dir"); ap.add_argument("--fixture"); a=ap.parse_args(); root=Path(a.root)
    if a.command=="scan": result=scan(root)
    elif a.command=="graph": result=dependency_graph(root)
    elif a.command=="drift":
        if not a.export_dir: ap.error("--export-dir is required")
        result=drift(Path(a.export_dir))
    elif a.command=="fuzz":
        text=Path(a.file).read_text(encoding="utf-8") if a.file else ""
        result=fuzz_cases(a.seed,a.count,text)
    elif a.command=="compat":
        if not a.file: ap.error("--file is required")
        result=compatibility(Path(a.file).read_text(encoding="utf-8"),a.profile)
    elif a.command=="live-verify":
        if not a.export_dir: ap.error("--export-dir is required")
        if verify_live is None: ap.error("live_notion_verify module not available")
        fetcher=None
        if a.fixture:
            body=Path(a.fixture).read_text(encoding="utf-8")
            fetcher=lambda _pid, b=body: b
        result=verify_live(Path(a.export_dir), fetcher=fetcher).to_dict()
    elif a.command=="pipeline": result=pipeline(root,a.seed,a.count,a.profile,Path(a.export_dir) if a.export_dir else None)
    else: result={"mode":"PROPOSAL_ONLY","findings":scan(root),"automatic_changes":False}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
