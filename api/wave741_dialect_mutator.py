"""Wave 741 Dialect Mutator — evolve organism tongue under fitness."""
from __future__ import annotations
import json, random, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave741_dialect_mutator.json"
SEED_PHRASES = ["silence compounds", "dna dreams organs", "lab gates neq aleph ci",
                "void twin awakens", "gravity pulls tasks"]
DEFAULT = {"module": "wave741_dialect_mutator", "wave": 741, "phrases": list(SEED_PHRASES), "epochs": []}


def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass


def _fitness(s: str) -> float:
    if not s: return 0.0
    uniq = len(set(s.lower()))
    length_pen = abs(len(s) - 24) / 24.0
    return round(uniq / max(len(s), 1) - 0.1 * length_pen, 4)


def _mutate(s: str, rng: random.Random) -> str:
    words = s.split()
    op = rng.choice(["swap", "suffix", "prefix", "split"])
    if op == "swap" and len(words) >= 2:
        i, j = rng.sample(range(len(words)), 2)
        words[i], words[j] = words[j], words[i]
        return " ".join(words)
    if op == "suffix":
        return (s + " " + rng.choice(["·", "∞", "void", "seal", "pulse"])).strip()
    if op == "prefix":
        return (rng.choice(["ix", "still", "soft", "live"]) + " " + s).strip()
    if op == "split" and len(words) >= 2:
        return " · ".join(words)
    return s


def coherence_vitals():
    st = _load()
    return {"wave": 741, "module": "wave741_dialect_mutator", "ok": True,
            "phrases": len(st.get("phrases") or []), "epochs": len(st.get("epochs") or [])}


def resonates_with():
    return ["wave710_dream_choir", "wave736_silent_broadcast_lattice", "wave727_metaphor_forge"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "mutate":
        seed = str(req.get("seed") or "")
        rng = random.Random(seed or hashlib.sha256(json.dumps(st.get("phrases")).encode()).hexdigest())
        phrases = list(st.get("phrases") or SEED_PHRASES)
        base = rng.choice(phrases)
        child = _mutate(base, rng)
        score, parent_score = _fitness(child), _fitness(base)
        kept = child if score >= parent_score else base
        if kept not in phrases:
            phrases.append(kept)
        st["phrases"] = phrases[-48:]
        st["last"] = {"parent": base, "child": child, "kept": kept, "score": max(score, parent_score)}
        _save(st)
        return {"status": "mutated", **st["last"], **coherence_vitals()}
    if action == "epoch":
        ep = {"label": str(req.get("label") or "dialect")[:48],
              "phrases": list(st.get("phrases") or [])[:12],
              "ts": datetime.now(timezone.utc).isoformat()}
        epochs = st.setdefault("epochs", [])
        epochs.append(ep)
        st["epochs"] = epochs[-32:]
        _save(st)
        return {"status": "epoch", "epoch": ep, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "mutate"}), indent=2))
