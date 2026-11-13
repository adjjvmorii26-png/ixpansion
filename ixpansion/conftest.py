import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Keep this subproject's sibling packages ahead of similarly named modules
# in the parent monorepo (for example, the root-level agents.py).
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
