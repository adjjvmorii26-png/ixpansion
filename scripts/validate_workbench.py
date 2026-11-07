from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    ".workbench/plugin-registry.yaml",
    "docs/LOCAL_WORKBENCH.md",
    "docs/PLUGIN_CAPABILITY_MATRIX.md",
    "skills/workbench-orchestrator/SKILL.md",
    "skills/plugin-adapter-contract/SKILL.md",
    "skills/repository-audit/SKILL.md",
    "skills/evidence-ledger/SKILL.md",
]
missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
if missing:
    print("FAIL: missing required files:")
    print("\n".join(missing))
    sys.exit(1)
for path in REQUIRED:
    if not (ROOT / path).read_text(encoding="utf-8").strip():
        print(f"FAIL: empty file: {path}")
        sys.exit(1)
print(f"PASS: {len(REQUIRED)} required files exist and are non-empty")
