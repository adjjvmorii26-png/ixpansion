import hashlib, json, tempfile, unittest
from pathlib import Path
from skill_lab import compatibility, drift, fuzz_cases, graph, patch_plan, scan, sha256

class SkillLabTests(unittest.TestCase):
    def test_frontmatter_scan_detects_missing_description(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"demo"; p.mkdir()
            (p/"SKILL.md").write_text("---\nname: demo\n---\nBody")
            self.assertIn("DESCRIPTION_MISSING",[x["code"] for x in scan(Path(d))])

    def test_graph_flags_missing_dependency(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a"; p.mkdir()
            (p/"SKILL.md").write_text("---\nname: alpha\ndescription: test\ndepends_on: ghost\n---\n")
            g=graph(Path(d))
            self.assertEqual(g["edges"][0]["status"],"MISSING_TARGET")

    def test_graph_detects_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            for name,dep in [("a","b"),("b","a")]:
                p=Path(d)/name; p.mkdir()
                (p/"SKILL.md").write_text(f"---\nname: {name}\ndescription: test\ndepends_on: {dep}\n---\n")
            self.assertTrue(graph(Path(d))["cycles"])

    def test_fuzz_is_deterministic_and_bounded(self):
        a=fuzz_cases("hello",1337,12); b=fuzz_cases("hello",1337,12)
        self.assertEqual(a,b); self.assertEqual(len(a),12)
        self.assertLessEqual(len(fuzz_cases("x",1,999)),256)

    def test_compatibility_catches_platform_leak(self):
        result=compatibility("---\nname: x\ndescription: y\n---\nuse mcp__secret", "portable")
        self.assertEqual(result["status"],"WARN")

    def test_drift_detects_modified_export(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/"seed_snapshot.md").write_text("seed")
            (p/"SKILL.md").write_text("changed")
            (p/"provenance.json").write_text(json.dumps({"source_sha256":sha256("seed"),"export_sha256":sha256("original")}))
            self.assertIn("EXPORT_DRIFT",[x["code"] for x in drift(p)])

    def test_repair_plan_is_proposal_only(self):
        plan=patch_plan([{"code":"FM_MISSING"}])
        self.assertEqual(plan["mode"],"PROPOSAL_ONLY")
        self.assertTrue(plan["mutations"])

if __name__=="__main__": unittest.main()
