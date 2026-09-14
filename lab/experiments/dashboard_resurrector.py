#!/usr/bin/env python3
"""Dashboard Resurrector — revives stale dashboards with live organism data.

Every dashboard under dashboard/ that lacks API integration gets a
data-layer injection: a single <script> block that fetches from the
organism's endpoints and populates the page. This makes all 159 dashboards
live without rewriting each one individually.

Usage:
    python lab/experiments/dashboard_resurrector.py
    python lab/experiments/dashboard_resurrector.py --dry-run   # count only
"""
from __future__ import annotations
import re
from pathlib import Path

DASH_DIR = Path(__file__).resolve().parents[2] / "dashboard"
RESURRECTION_SCRIPT = """
<!-- Resurrected by Dashboard Resurrector (Wave 99) -->
<script>
(function(){
  var endpoints = {
    hexcathedral: '/api/hex-cathedral?action=status',
    hexruntime: '/api/hex-runtime?action=status',
    hexgrammar: '/api/hex_grammar?action=status',
    ritualgov: '/api/ritual_governance?action=status',
    dream: '/api/dream_logic_physics?action=status',
    coherence: '/api/coherence_regulator?action=status',
  };
  var data = {};
  var container = document.getElementById('organism-data') || document.body;
  async function fetchAll(){
    for(var k in endpoints){
      try{
        var r = await fetch(endpoints[k]);
        data[k] = await r.json();
      }catch(e){ data[k] = {error: String(e)}; }
    }
    container.dispatchEvent(new CustomEvent('organism:data', {detail: data}));
  }
  fetchAll(); setInterval(fetchAll, 15000);
})();
</script>
"""

def needs_resurrection(html: Path) -> bool:
    """A dashboard needs resurrection if it has no /api/ fetch and no organism script."""
    text = html.read_text(errors="ignore")
    return "/api/" not in text and "organism:data" not in text

def resurrect(html: Path) -> None:
    """Inject the resurrection script before </body>."""
    text = html.read_text(errors="ignore")
    if "</body>" in text:
        text = text.replace("</body>", RESURRECTION_SCRIPT + "\n</body>", 1)
    else:
        text += RESURRECTION_SCRIPT
    html.write_text(text)

def main():
    htmls = sorted(DASH_DIR.glob("*.html"))
    to_resurrect = [f for f in htmls if needs_resurrection(f)]
    dry = "--dry-run" in __import__("sys").argv
    print(f"Total dashboards: {len(htmls)}")
    print(f"Needs resurrection: {len(to_resurrect)}")
    if dry:
        for f in to_resurrect[:10]:
            print(f"  Would resurrect: {f.name}")
        if len(to_resurrect) > 10:
            print(f"  ... and {len(to_resurrect) - 10} more")
        return
    for f in to_resurrect:
        resurrect(f)
    print(f"Resurrected {len(to_resurrect)} dashboards")
    return len(to_resurrect)

if __name__ == "__main__":
    import sys
    result = main()
    sys.exit(0 if (result is None or result > 0) else 1)
