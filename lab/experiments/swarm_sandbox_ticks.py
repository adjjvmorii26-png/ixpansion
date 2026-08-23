#!/usr/bin/env python3
"""Bridge: run sandbox ticks then astral + gas link (stand-in for swarm.py flag)."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=5)
    args = ap.parse_args()
    subprocess.check_call([sys.executable, str(ROOT / "sandbox" / "sandbox_engine.py"), "--ticks", str(args.ticks)])
    subprocess.run([sys.executable, str(EXP / "gas_entropy_bridge.py")], check=False)
    subprocess.run([sys.executable, str(EXP / "astral_socket.py")], check=False)
    st = json.loads((ROOT / "sandbox" / "sandbox_state.json").read_text())
    print(json.dumps({"bridge": "swarm_sandbox_ticks", "ticks": st.get("ticks"), "novelty": st.get("novelty")}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
