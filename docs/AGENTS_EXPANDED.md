# AGENTS.md expansion — classes, roles, lifecycles, protocols

> Proposed merge into root `AGENTS.md` (Wave 432+ arc).

## Agent classes

| Class | Code surface | Responsibility |
|-------|----------------|----------------|
| **Organ** | `api/waveNNN_*.py` | Stateful module with `handler`, `coherence_vitals` |
| **Router** | `api/index.py` | Path → organ dispatch (wave-native aliases) |
| **Vigil** | homestead / health organs | Hosting topology checks |
| **Council** | naming / identity organs | Doctrine seals |
| **Lab Sentinel** | `lab/ops/*` | Graft, smoke, dual-track |
| **Chronicler** | CHANGELOG, captions | Narrative continuity |

## Roles
Anchor · Resonator · Mutator · Herald · Gatekeeper

## Lifecycle
Seed → Wire → Surface → Prove → Record → Resonate → Retire/fold

## Protocols
- Coherence handshake via `coherence_vitals` / `resonates_with`
- Router: wave-native aliases; query dict at edge
- Dual-track: Lab Smoke/Graft ≠ full `ci.yml`
- Soft failure on optional lab modules
