import json, tempfile, unittest
from pathlib import Path
from skill_lab import compatibility, dependency_graph, digest, drift, fuzz_cases, pipeline, scan, diagnose

class FoundryTests(unittest.TestCase):
    def make_skill(self,root,folder,name,deps=""):
        p=root/folder; p.mkdir(parents=True)
        dep=("depends_on: ["+deps+"]\n") if deps else ""
        (p/"SKILL.md").write_text("---\nname: "+name+"\ndescription: test\n"+dep+"---\n",encoding="utf-8")
    def test_scan_finds_missing_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"sample"; p.mkdir(); (p/"SKILL.md").write_text("---\nname: sample\n---\n")
            self.assertIn("DESCRIPTION_MISSING",[x["code"] for x in scan(Path(tmp))])
    def test_graph_finds_missing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_skill(Path(tmp),"sample","sample","absent")
            self.assertEqual(dependency_graph(Path(tmp))["edges"][0]["status"],"MISSING_TARGET")
    def test_graph_detects_cycle_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.make_skill(root,"a","alpha","beta"); self.make_skill(root,"b","beta","alpha")
            g=dependency_graph(root); self.assertEqual(len(g["cycles"]),1)
            self.assertIn("DEPENDENCY_CYCLE",[e["status"] for e in g["edges"]])
    def test_fuzz_is_repeatable_bounded_and_carries_excerpt(self):
        self.assertEqual(fuzz_cases(1337,12,"abc"),fuzz_cases(1337,12,"abc"))
        self.assertEqual(len(fuzz_cases(1,900)),256)
        self.assertEqual(fuzz_cases(1,1,"abc")[0]["input_excerpt"],"abc")
    def test_compatibility_warns_on_platform_leak(self):
        self.assertEqual(compatibility("name: test mcp__adapter","portable")["status"],"WARN")
    def test_drift_detects_export_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/"seed_snapshot.md").write_text("seed"); (p/"SKILL.md").write_text("changed")
            (p/"provenance.json").write_text(json.dumps({"source_sha256":digest("seed"),"export_sha256":digest("old")}))
            self.assertIn("EXPORT_DRIFT",[x["code"] for x in drift(p)])
    def test_failure_pattern_corpus_maps_findings(self):
        self.assertEqual(diagnose([{"code":"MISSING_TARGET"}])[0]["pattern_id"],"FP-002")
    def test_pipeline_is_ordered_and_proposal_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.make_skill(root,"a","alpha","missing")
            r=pipeline(root,1337,8); self.assertEqual(r["sequence"][0],"DISCOVER")
            self.assertEqual(r["sequence"][-1],"EXPORT_REVIEW"); self.assertFalse(r["automatic_changes"])
            self.assertTrue(r["failure_pattern_matches"])

if __name__=="__main__": unittest.main()
