#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
THEMES = {"stratum": "ELRP band refuses silent act", "chronoforge": "Epoch transitions need ceremony", "monolith": "Glyphs outlive binaries", "orbit": "Occultation gates ethics_ok"}
def probe(theme):
    frames = [
        {"t": "0.0s", "role": "hook", "text": f"IXPANSION · {theme.upper()}", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": THEMES.get(theme, "Proof over spectacle"), "style": "magenta_dim"},
    ]
    se = REPO / "lab" / "STRATUM_ENGINE" / "EMERGENT_LAYER" / "reasoning" / "reason_engine.py"
    if se.exists():
        r = subprocess.run([sys.executable, str(se)], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout or "{}")
            frames.append({"t": "5.0s", "role": "live", "text": f"ELRP → {d.get('action','?')} · band {d.get('band')}", "style": "cyan"})
        except json.JSONDecodeError: pass
    frames.append({"t": "8.0s", "role": "cta", "text": "@CoodingLooop · proof ledger not vanity", "style": "dim"})
    return {"ok": True, "project": "caption_lattice", "theme": theme, "frames": frames, "ts": datetime.now(timezone.utc).isoformat(), "audio": None}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--theme", default="stratum", choices=list(THEMES))
    args = ap.parse_args(); out = probe(args.theme)
    out_dir = REPO / "content_output" / "captions"; out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"lattice_{args.theme}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2)+"\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
