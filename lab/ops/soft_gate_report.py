#!/usr/bin/env python3
"""Soft Gate Report — lab vs ALEPH one-pager."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    smoke = subprocess.run([sys.executable, str(REPO / "lab" / "smoke_lab.py")], capture_output=True, text=True, timeout=90)
    try: smoke_ok = bool(json.loads(smoke.stdout or "{}").get("ok"))
    except json.JSONDecodeError: smoke_ok = smoke.returncode == 0
    md = f"""# Soft Gate Report\n\n**ts:** {datetime.now(timezone.utc).isoformat()}\n\n| Gate | Status |\n|------|--------|\n| Lab smoke (local) | {"PASS" if smoke_ok else "FAIL"} |\n| Lab track branch | lab/chrono-forge-wave |\n| ALEPH track | main · full ci.yml |\n| Vercel / Pages | ALEPH deploy surface (not lab gate) |\n\n## Doctrine\n- Lab Smoke + Lab Graft define organism readiness\n- Full monorepo CI is ALEPH track\n- Absence is structure · silence is the product surface\n\n```bash\npython lab/ops/lab_suite.py\npython lab/ops/soft_gate_report.py\n```\n"""
    path = REPO / "docs" / "SOFT_GATE_REPORT.md"
    path.write_text(md)
    print(json.dumps({"ok": True, "smoke": smoke_ok, "wrote": str(path)}, indent=2))
    return 0 if smoke_ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
