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
            r=pipeline(root,1337,8); self.assertEqual(r["executed_stages"][0],"DISCOVER")
            self.assertIn("FUZZ_CASE_GENERATION",r["executed_stages"])
            self.assertIn("REGRESSION_EXECUTION",r["not_run_stages"])
            self.assertIn("LIVE_NOTION_VERIFY",r["not_run_stages"])
            self.assertFalse(r["automatic_changes"])
            self.assertNotIn("ORPHAN_SKILL",[x["code"] for x in r["scan_findings"]])
            self.assertTrue(r["failure_pattern_matches"])


    def test_pipeline_does_not_claim_unrun_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.make_skill(root,"a","alpha")
            result=pipeline(root)
            self.assertNotIn("REGRESSION_EXECUTION",result["executed_stages"])
            self.assertNotIn("LIVE_NOTION_VERIFY",result["executed_stages"])
            self.assertIsNone(result["drift_findings"])
            self.assertIn("EXPORT_REVIEW",result["not_run_stages"])


    def test_pipeline_runs_local_drift_only_when_export_dir_is_supplied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"skills"; root.mkdir()
            self.make_skill(root,"a","alpha")
            export=Path(tmp)/"export"; export.mkdir()
            (export/"seed_snapshot.md").write_text("seed",encoding="utf-8")
            (export/"SKILL.md").write_text("export",encoding="utf-8")
            (export/"provenance.json").write_text(json.dumps({
                "source_sha256":digest("seed"),"export_sha256":digest("export")
            }),encoding="utf-8")
            result=pipeline(root,export_dir=export)
            self.assertIn("LOCAL_EXPORT_DRIFT_CHECK",result["executed_stages"])
            self.assertEqual(result["drift_findings"],[])
            self.assertNotIn("EXPORT_REVIEW",result["not_run_stages"])
            self.assertIn("EXPORT_PROMOTION_REVIEW",result["not_run_stages"])

    def test_root_compatibility_entrypoint_uses_canonical_implementation(self):
        import importlib.util
        root_file=Path(__file__).resolve().parents[1]/"skill_lab.py"
        spec=importlib.util.spec_from_file_location("foundry_root_compat",root_file)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(module.digest("same"),digest("same"))
        self.assertEqual(module.fuzz_cases(4,3),fuzz_cases(4,3))

    def test_pipeline_maps_compatibility_leak_to_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.make_skill(root,"a","alpha")
            (root/"a"/"SKILL.md").write_text("---\nname: alpha\ndescription: test\n---\nmcp__adapter\n")
            r=pipeline(root)
            self.assertIn("PROFILE_FORBIDDEN",[x["code"] for x in r["scan_findings"]])
            self.assertIn("FP-004",[x["pattern_id"] for x in r["failure_pattern_matches"]])

if __name__=="__main__": unittest.main()
