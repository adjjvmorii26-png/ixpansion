"""Lab Graft Deploy — deploys lab paths to GitHub Pages."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
GH_PAGES = ROOT / "docs" / "campaigns"

def graft_lab_paths():
    """Copy lab documentation to gh-pages deploy directory."""
    lab_files = []
    for subdir in ["CHRONOFORGE", "STRATUM_ENGINE", "MONOLITH_STACK", "chronoweave", "paradox_forge", "polygenesis", "chronoforge"]:
        src = ROOT / "lab" / subdir
        if src.exists():
            for f in src.rglob("*.md"):
                lab_files.append(str(f))

    deploy_manifest = {
        "grafted_at": datetime.now(timezone.utc).isoformat(),
        "lab_paths": lab_files,
        "count": len(lab_files),
        "status": "grafted",
    }
    manifest_path = GH_PAGES / "lab_graft_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(deploy_manifest, indent=2))
    return deploy_manifest

if __name__ == "__main__":
    result = graft_lab_paths()
    print(f"✓ Grafted {result['count']} lab paths to gh-pages")
    print(f"  Manifest: {manifest_path}")
