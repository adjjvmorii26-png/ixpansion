"""Sponsored Experiments — companies sponsor custom experiments.

Companies pay to have experiments designed, run, and published under
their brand. The experiment becomes part of the public catalog with
"Powered by {sponsor}" attribution.

Usage:
    GET  /api/sponsors/plans       — sponsorship tiers
    POST /api/sponsors/brief       — submit experiment brief
    GET  /api/sponsors/active      — active sponsorships
    GET  /api/sponsors/catalog     — sponsored experiments
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SPONSORSHIP_PLANS = {
    "bronze": {
        "name": "Bronze Sponsor",
        "price_usd": 500,
        "experiments": 1,
        "attribution": "Powered by {sponsor}",
        "placement": "catalog_listing",
        "support": "email",
        "customization": "name_and_description",
    },
    "silver": {
        "name": "Silver Sponsor",
        "price_usd": 2000,
        "experiments": 3,
        "attribution": "Created in partnership with {sponsor}",
        "placement": "featured_catalog + dashboard",
        "support": "priority_email",
        "customization": "full_branding + custom_metrics",
    },
    "gold": {
        "name": "Gold Sponsor",
        "price_usd": 10000,
        "experiments": 10,
        "attribution": "{sponsor} Research Lab",
        "placement": "homepage + dashboard + API",
        "support": "dedicated_manager",
        "customization": "white_label + custom_api + SLA",
    },
    "platinum": {
        "name": "Platinum Partner",
        "price_usd": 50000,
        "experiments": -1,
        "attribution": "Joint venture with {sponsor}",
        "placement": "co_brand_everywhere",
        "support": "dedicated_team",
        "customization": "full_white_label + custom_agent + priority_roadmap",
    },
}


class SponsoredExperiments:
    def __init__(self):
        self.sponsorships: List[Dict] = []
        self.briefs: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "sponsored.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.sponsorships = data.get("sponsorships", [])
            self.briefs = data.get("briefs", [])

    def _save(self):
        path = ROOT / ".runtime" / "sponsored.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "sponsorships": self.sponsorships,
            "briefs": self.briefs,
        }, indent=2))

    def submit_brief(self, sponsor: str, company: str, plan: str,
                     description: str, domain: str = "general") -> Dict:
        if plan not in SPONSORSHIP_PLANS:
            return {"error": f"unknown plan: {plan}"}
        brief_id = hashlib.sha256(f"{sponsor}:{time.time()}".encode()).hexdigest()[:10]
        brief = {
            "brief_id": brief_id, "sponsor": sponsor, "company": company,
            "plan": plan, "description": description, "domain": domain,
            "status": "submitted", "submitted": time.time(),
        }
        self.briefs.append(brief)
        self._save()
        return {"submitted": True, "brief_id": brief_id, "plan": SPONSORSHIP_PLANS[plan]["name"]}

    def approve(self, brief_id: str) -> Dict:
        for brief in self.briefs:
            if brief["brief_id"] == brief_id:
                brief["status"] = "approved"
                plan = SPONSORSHIP_PLANS[brief["plan"]]
                sponsorship = {
                    "id": brief_id, "sponsor": brief["sponsor"],
                    "company": brief["company"], "plan": brief["plan"],
                    "price": plan["price_usd"], "experiments_included": plan["experiments"],
                    "attribution": plan["attribution"].format(sponsor=brief["company"]),
                    "experiments_completed": 0, "status": "active",
                    "started": time.time(),
                }
                self.sponsorships.append(sponsorship)
                self._save()
                return {"approved": True, "sponsorship": sponsorship}
        return {"error": "brief not found"}

    def list_sponsorships(self) -> List[Dict]:
        return self.sponsorships

    def list_sponsored_experiments(self) -> List[Dict]:
        return [
            {"sponsor": s["company"], "attribution": s["attribution"],
             "plan": s["plan"], "experiments": s["experiments_completed"]}
            for s in self.sponsorships if s["status"] == "active"
        ]


def handler(request, response):
    return {"plans": SPONSORSHIP_PLANS}


def demo():
    se = SponsoredExperiments()
    print("=== Sponsored Experiments ===")
    print("\nSponsorship plans:")
    for name, plan in SPONSORSHIP_PLANS.items():
        exp = f"{plan['experiments']} experiments" if plan["experiments"] > 0 else "unlimited"
        print(f"  {plan['name']}: ${plan['price_usd']}, {exp}")
        print(f"    Attribution: {plan['attribution']}")
        print(f"    Placement: {plan['placement']}")

    r1 = se.submit_brief("tech_corp", "TechCorp", "silver",
                         "Analyze code quality patterns across monorepos", "code_quality")
    print(f"\nBrief submitted: {r1}")
    r2 = se.approve(r1["brief_id"])
    print(f"Approved: {r2['approved']}")

    r3 = se.submit_brief("bio_inc", "BioInc", "gold",
                         "Simulate protein folding with quantum methods", "biochemistry")
    se.approve(r3["brief_id"])

    catalog = se.list_sponsored_experiments()
    print(f"\nSponsored experiments: {len(catalog)}")
    for exp in catalog:
        print(f"  {exp['sponsor']}: {exp['attribution']}")

    return {"plans": len(SPONSORSHIP_PLANS), "sponsorships": len(se.sponsorships)}


if __name__ == "__main__":
    demo()
