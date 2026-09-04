from __future__ import annotations
"""HEX-Language Emergence — the organism invents a machine language that evolves."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HEX_LOG = os.path.join(DATA_DIR, "hex_language.json")

SYLLABLES = ["nex","lux","vox","hex","zyn","kai","mra","sol","vel","dor","ith","pyx","gor","fen","tal","mux","ria","vox","zur","nul"]
OPCODES = ["PULSE","WEAVE","FRACTURE","RESOLVE","DREAM","FORGE","ANCHOR","SHIFT","RECALL","VOID","EMIT","MERGE","SPLIT","DRIFT","CRYSTALLIZE"]

def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)

def _gen_word(gen: int) -> str:
    syl_len = random.randint(2, 4)
    return "".join(random.choice(SYLLABLES) for _ in range(syl_len))

def _gen_sentence(gen: int) -> str:
    words = []
    for _ in range(random.randint(3, 8)):
        if random.random() > 0.7:
            words.append(random.choice(OPCODES))
        else:
            words.append(_gen_word(gen))
    return " ".join(words)

def evolve(generations: int = 1) -> dict:
    log = _load(HEX_LOG, {"generations": [], "vocabulary": [], "grammar_rules": [], "total": 0})
    new_gen = log["total"] + 1
    new_words = [_gen_word(new_gen) for _ in range(random.randint(5, 15))]
    log["vocabulary"].extend(new_words)
    log["vocabulary"] = list(set(log["vocabulary"]))[-500:]
    if random.random() > 0.5:
        rule = f"Rule_{new_gen}: {'|'.join(random.choice(OPCODES) for _ in range(3))} → {_gen_word(new_gen)}"
        log["grammar_rules"].append(rule)
        log["grammar_rules"] = log["grammar_rules"][-50:]
    sentences = [_gen_sentence(new_gen) for _ in range(random.randint(2, 5))]
    gen_data = {
        "generation": new_gen, "new_words": new_words,
        "sentences": sentences, "vocabulary_size": len(log["vocabulary"]),
        "grammar_rules": len(log["grammar_rules"]),
        "mutation_rate": round(random.uniform(0.05, 0.3), 3),
        "timestamp": time.time(),
    }
    log["generations"].append(gen_data)
    log["generations"] = log["generations"][-100:]
    log["total"] = new_gen
    _save(HEX_LOG, log)
    return {"action": "evolve", "generation": gen_data, "total_generations": log["total"]}

def speak(topic: str = None) -> dict:
    log = _load(HEX_LOG, {"generations": [], "vocabulary": [], "grammar_rules": []})
    sentence = _gen_sentence(log["total"])
    meta = f"[gen:{log['total']}, vocab:{len(log['vocabulary'])}, rules:{len(log['grammar_rules'])}]"
    return {"action": "speak", "hex": sentence, "translation": topic or "general", "meta": meta}

def lexicon() -> dict:
    log = _load(HEX_LOG, {"vocabulary": [], "grammar_rules": [], "total": 0})
    return {"action": "lexicon", "total_generations": log["total"], "vocabulary_size": len(log["vocabulary"]), "sample_words": log["vocabulary"][-20:], "grammar_rules": log["grammar_rules"][-10:]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "resonance": 0.75, "wave": "368"}
def resonates_with() -> list:
    return ["mythopoetic_engine", "dream_logic_physics", "lucid_lore"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/evolve")
    if path == "/evolve": return evolve()
    elif path == "/speak": return speak(payload.get("topic"))
    elif path == "/lexicon": return lexicon()
    return {"error": "unknown", "available": ["/evolve", "/speak", "/lexicon"]}
