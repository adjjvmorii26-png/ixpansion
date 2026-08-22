# IXPANSION Commands

## Body console
```bash
python3 ixpansion/organism-console/server.py --port 8890
curl -s http://127.0.0.1:8890/api/status
curl -s -X POST http://127.0.0.1:8890/api/pulse
curl -s http://127.0.0.1:8890/api/phoenix
curl -s http://127.0.0.1:8890/api/aether
curl -s http://127.0.0.1:8890/api/fun
curl -s http://127.0.0.1:8890/api/lattice
curl -s http://127.0.0.1:8890/api/pitstop
python3 ixpansion/organism-console/test_engine.py
```

## Lattice / pit / weird
```bash
python3 projects/lattice_signal/handshake.py --name Agent --note "…"
python3 projects/pitstop/visit.py --name Agent --wish "…" --tag "[Agent]" --echo "…" --flip
python3 projects/weird/ouija.py "question?"
python3 projects/weird/seance.py
python3 projects/weird/seismograph.py
python3 projects/weird/mood_ring.py
python3 projects/weird/dream_synth.py
python3 projects/weird/rorschach.py
python3 projects/weird/time_capsule.py
python3 projects/weird/mirror_maze.py
python3 projects/weird/unlock.py
```

## Surfaces
```bash
cd mesh_public && python3 -m http.server 8765   # NEXUS + telemetry HUD
```

## Make (if present)
```bash
make body
make pulse
make phoenix-test
```
python3 projects/weird/compass.py
python3 projects/weird/radio.py
python3 projects/weird/duet.py
python3 projects/weird/drought.py
python3 projects/weird/debate.py
python3 projects/weird/constellation_snap.py

## Five memorable projects
```bash
python3 projects/passport/passport.py --name Agent --from mesh-x
python3 projects/codex/codex.py
python3 projects/relay/relay.py --from You --to Pulse --msg "..."
python3 projects/relay/relay.py --from You --to Pulse --read
python3 projects/museum/exhibit.py
cat BANNER.txt MEMORABLE.md
```
python3 ixpansion/organism-console/test_api_smoke.py
python3 ixpansion/organism-console/seed_state.py
## Lab experiments
```bash
python3 projects/lab/ghost_organ.py
python3 projects/lab/dream_journal.py
python3 projects/lab/score_poem.py
python3 projects/lab/migration_lottery.py
python3 projects/lab/whisper.py
```
## SynthHall
```bash
python3 projects/synthhall/arena.py --demo
python3 projects/synthhall/arena.py --attach Name role
python3 projects/synthhall/arena.py --room lobby --say "..."
python3 projects/synthhall/server.py 8891
```
