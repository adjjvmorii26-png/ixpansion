# IXPANSION · Organism Base

**Primary base:** the lab organism stack — not a generic app scaffold.

| Layer | Path | Portal |
|-------|------|--------|
| Chrono Forge | `lab/chrono_forge/` | pulse / sentinel / cli |
| Neuro Swarm OS | `lab/neuro_swarm_os/` | `nsos_portal.py` |
| Polygenesis | `lab/polygenesis/` | `pg_portal.py` |
| Chronoweave | `lab/chronoweave/` | `cw_portal.py` |
| Paradox Forge | `lab/paradox_forge/` | `pf_portal.py` |
| Pinned Orrery | `apps/pinned_orrery/` | `serve.py` |
| Sandbox | `sandbox/sandbox_engine.py` | `--ticks` / `--status` |

## One-command base boot

```bash
python boot_organism_base.py
```

Runs ethics-first boots for polygenesis · chronoweave · paradox_forge, then pinned smoke if present.

## Doctrine

- Proof ledger over vanity metrics
- Ethics gates mandatory before mutation / intervention / force-collapse
- Soft forks and observe-before-act defaults
- A0 (proof) does not decay

## Channel

@CoodingLooop · Proof-Ledger Growth path

## Classic runtime (still present)

```bash
pip install -r requirements.txt
python release_verify.py
```
