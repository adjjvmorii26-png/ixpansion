import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from tools.generators.agent_gen import generate


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: spawn_agent.py NAME DESTINATION")
    print(generate(sys.argv[1], Path(sys.argv[2])))
