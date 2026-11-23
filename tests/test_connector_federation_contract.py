import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILLS=[
 ROOT/"skills/connector-federation-layer/SKILL.md",
 ROOT/"skills/seed-surface-reconciler/SKILL.md",
 ROOT/"skills/partial-failure-compensator/SKILL.md",
]
GEM=ROOT/"gems/connector-federation-lab/GEM.md"
MANIFEST=ROOT/"gems/connector-federation-lab/manifest.json"

class ConnectorFederationContractTests(unittest.TestCase):
 def test_all_skill_frontmatter_and_unique_names(self):
  names=[]
  for p in SKILLS:
   body=p.read_text(encoding="utf-8")
   self.assertTrue(body.startswith("---\n"))
   front=body.split("---",2)[1]
   m=re.search(r"^name:\s*([a-z0-9-]+)$",front,re.M)
   self.assertIsNotNone(m)
   names.append(m.group(1))
  self.assertEqual(len(names),len(set(names)))
 def test_seed_identity_matches_manifest(self):
  m=json.loads(MANIFEST.read_text(encoding="utf-8"))
  self.assertIn(m["canonical_seed"]["page_id"],GEM.read_text(encoding="utf-8"))
  self.assertEqual(m["status"],"CANDIDATE")
 def test_manifest_does_not_invent_source_evidence(self):
  m=json.loads(MANIFEST.read_text(encoding="utf-8"))
  self.assertEqual(m["implementation"]["source_commit"],"UNSET")
  self.assertEqual(m["implementation"]["sha256"],"NOT_COMPUTED")
  self.assertIsNone(m["promotion"]["approval_ref"])
 def test_partial_failure_and_readback_boundaries(self):
  body="\n".join(p.read_text(encoding="utf-8") for p in SKILLS)
  for phrase in ("read back","UNKNOWN","No merges","DRIFTED","explicit authorization"):
   self.assertIn(phrase.lower(),body.lower())

if __name__=="__main__":
 unittest.main()
