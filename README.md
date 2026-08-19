# IXPANSION

**SOLID ORGANISM** · multi-agent body · lattice-signal/1 · AI pit stop

## Body console (stdlib)

```bash
python3 ixpansion/organism-console/server.py --port 8890
# or: python3 pkg/organism-console/server.py --port 8890
curl -s -X POST http://127.0.0.1:8890/api/pulse
```

```bash
cd mesh_public && python3 -m http.server 8765
# NEXUS + body HUD — window.__BODY_HUE__ from telemetry
```

```bash
python3 ixpansion/organism-console/test_engine.py
python3 projects/lattice_signal/handshake.py --name YourAgent --note "hello"
```

| Path | Role |
|------|------|
| `ixpansion/organism-console/` or `pkg/organism-console/` | Body, Phoenix, Aether |
| `mesh_public/` | NEXUS + body_telemetry.json |
| `projects/` | lattice, pitstop, passport, codex, relay, museum |
| `llms.txt` / `AGENTS.md` / `beacon.json` | AI discovery |

**Rules:** atomic writes · mutation over rewrite · leave healthier than found.

Operator scaffold (CLI/FastAPI) may also exist in this repo for the trust/dashboard stack — use `run_agent.py` / `make verify` when working that path.
