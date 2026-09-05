"""
Lucid Shrine — Wave 384
A hall of runs. Any player may offer their save code to the Shrine; the
organism decodes it, scores the run, and inscribes it in the hall of runs
with a rank. Saves become offerings; play becomes legacy.

Persistence is GitHub-backed when IXP_GH_TOKEN is set in the environment
(offerings become real commits to data/lucid_shrine.json), with a local
fallback for sandbox runs.
"""
import json, time, hashlib, os, base64, urllib.parse, urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SHRINE_LOG = os.path.join(DATA_DIR, "lucid_shrine.json")
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
GH_REPO = "adjjvmorii26-png/ixpansion"
GH_PATH = "data/lucid_shrine.json"
GH_BRANCH = "main"

TITLES = [
    "Wayfarer", "Dream Touched", "Paradox Dancer", "Realm Walker",
    "Warden Slayer", "Coherence Sage", "Lucid Veteran", "Co-Pilot of the Organism",
    "Echo of the First Wave", "Warden of All Realms", "Mythic Sovereign",
]
MAX_RUNS = 100


def _gh_api(method: str, url: str, payload: dict = None) -> dict:
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + GH_TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    data = json.dumps(payload).encode() if payload is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode() or "{}")}
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode() or "{}")
        except Exception:
            pass
        return {"ok": False, "status": e.code, "body": body}


def _gh_read() -> dict:
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{urllib.parse.quote(GH_PATH)}?ref={GH_BRANCH}"
    r = _gh_api("GET", url)
    if not r["ok"]:
        return {"runs": [], "sha": None}
    try:
        content = json.loads(base64.b64decode(r["body"]["content"]).decode())
    except Exception:
        return {"runs": [], "sha": None}
    return {"runs": content.get("runs", []), "sha": r["body"].get("sha")}


def _gh_write(runs: list, sha: str = None) -> bool:
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{urllib.parse.quote(GH_PATH)}"
    payload = {
        "message": "SHRINE OFFERING — a run inscribed",
        "content": base64.b64encode(json.dumps({"runs": runs}, indent=2).encode()).decode(),
        "branch": GH_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    r = _gh_api("PUT", url, payload)
    return r["ok"]


def _load_local(d=None):
    for _p in (SHRINE_LOG, os.path.join("/tmp", os.path.basename(SHRINE_LOG))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return {"runs": []}


def _save_local(runs):
    try:
        os.makedirs(os.path.dirname(SHRINE_LOG), exist_ok=True)
        with open(SHRINE_LOG, "w") as f:
            json.dump({"runs": runs}, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(SHRINE_LOG)), "w") as f:
            json.dump({"runs": runs}, f, indent=2)


def _decode_blob(blob):
    if not blob:
        return None
    try:
        padded = blob + "=" * (-len(blob) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
    except Exception:
        return None


def _score(session) -> dict:
    wave = session.get("wave", 0)
    level = session.get("player_level", 1)
    cleared = len(session.get("realms_cleared", []) or [])
    treasures = session.get("treasures_found", 0)
    paradox = session.get("paradox_debt", 0)
    coherence = session.get("coherence", 0.5)
    score = (
        wave * 10
        + level * 50
        + cleared * 250
        + treasures * 25
        - paradox * 5
        + int(coherence * 25)
    )
    return {
        "score": max(0, int(score)),
        "wave": wave, "level": level, "realms_cleared": cleared,
        "treasures": treasures, "paradox_debt": paradox, "coherence": coherence,
    }


def _title_for(score: int) -> str:
    return TITLES[min(score // 150, len(TITLES) - 1)]


def _merge_run(runs: list, run: dict) -> list:
    runs = [r for r in runs if r.get("id") != run["id"]]
    runs.append(run)
    runs.sort(key=lambda r: (-r["score"], r["timestamp"]))
    return runs[:MAX_RUNS]


def offer(blob: str = None, name: str = "Wanderer", session_id: str = None) -> dict:
    session = _decode_blob(blob)
    if not session:
        return {"action": "offer", "error": "invalid save code"}
    stats = _score(session)
    run = {
        "id": (session_id or session.get("id") or hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:10]),
        "name": (name or "Wanderer")[:20],
        "title": _title_for(stats["score"]),
        "realm": session.get("realm", "unknown"),
        "status": session.get("status", "active"),
        "score": stats["score"],
        "wave": stats["wave"], "level": stats["level"],
        "realms_cleared": stats["realms_cleared"],
        "treasures": stats["treasures"],
        "paradox_debt": stats["paradox_debt"],
        "timestamp": time.time(),
    }
    # GitHub-backed persistence (serverless-safe), retry on 409 conflicts
    if GH_TOKEN:
        base, sha = _gh_read()["runs"], _gh_read()["sha"]
        merged = _merge_run(base, run)
        for attempt in range(4):
            if _gh_write(merged, sha):
                total = len(merged)
                rank = next((i + 1 for i, r in enumerate(merged) if r["id"] == run["id"]), None)
                return {"action": "offer", "run": run, "rank": rank, "total_inscribed": total,
                        "title": run["title"], "persisted": "github"}
            # conflict: re-read and retry
            base, sha = _gh_read()["runs"], _gh_read()["sha"]
            merged = _merge_run(base, run)
        return {"action": "offer", "run": run, "error": "shrine is busy; try again",
                "persisted": "retry_exhausted"}
    runs = _merge_run(_load_local().get("runs", []), run)
    _save_local(runs)
    rank = next((i + 1 for i, r in enumerate(runs) if r["id"] == run["id"]), None)
    return {"action": "offer", "run": run, "rank": rank, "total_inscribed": len(runs),
            "title": run["title"], "persisted": "local"}


def hall() -> dict:
    if GH_TOKEN:
        runs = _gh_read()["runs"]
        return {"action": "hall", "runs": runs[:20], "total": len(runs), "persisted": "github"}
    runs = _load_local().get("runs", [])
    return {"action": "hall", "runs": runs[:20], "total": len(runs), "persisted": "local"}


def rank(blob: str = None, session_id: str = None) -> dict:
    sid = session_id
    if not sid:
        session = _decode_blob(blob)
        sid = session.get("id") if session else None
    runs = _gh_read()["runs"] if GH_TOKEN else _load_local().get("runs", [])
    for i, r in enumerate(runs):
        if r.get("id") == sid:
            return {"action": "rank", "found": True,
                    "rank": i + 1, "total": len(runs),
                    "percentile": round((1 - i / max(len(runs), 1)) * 100, 1),
                    "run": r, "persisted": "github" if GH_TOKEN else "local"}
    return {"action": "rank", "found": False, "total": len(runs)}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/hall")
    if path == "/offer":
        return offer(payload.get("blob"), payload.get("name"), payload.get("session_id"))
    if path == "/hall":
        return hall()
    if path == "/rank":
        return rank(payload.get("blob"), payload.get("session_id"))
    return {"error": "unknown", "available": ["/offer", "/hall", "/rank"]}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "384", "module": "lucid_shrine"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
