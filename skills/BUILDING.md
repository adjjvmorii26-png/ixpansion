# IXPANSION Skill Registry and Building Contract

The repository contains portable skill instructions in `skills/` and the
IXPANSION toolkit extension under `codetools/plugins/`. Each `SKILL.md`
defines a reusable workflow; the registry below is the complete repository
inventory observed by the Skill Vitality gate.

## Repository Skill Manifest

| Skill | Purpose | Location |
|---|---|---|
| `ixpansion-wave-builder` | Build and validate evolution waves using isolated branches and approval-gated releases | `codetools/plugins/ixpansion-toolkit/skills/ixpansion-wave-builder` |
| `artifact-parity-gate` | Verify canonical artifacts and their derived copies without silent overwrites | `skills/artifact-parity-gate` |
| `antimemetic_weave` | Analyze absence patterns and negative-space relationships | `skills/r1/antimemetic_weave` |
| `blog_curator` | Create, classify, search, surface, and safely archive blog posts | `skills/r1/blog_curator` |
| `chrono_relay` | Analyze temporal mechanics, cyclic memory, and archive timelines | `skills/r1/chrono_relay` |
| `data_pipeline_asynchronous_engine` | Coordinate asynchronous data-pipeline actions | `skills/r1/data_pipeline_asynchronous_engine` |
| `dream_compiler` | Convert dream-state inputs into reviewable module and wave proposals | `skills/r1/dream_compiler` |
| `handler_handler_engine` | Coordinate handler-level organism actions | `skills/r1/handler_handler_engine` |
| `handler_meta_evolution_engine` | Analyze and propose bounded handler evolution | `skills/r1/handler_meta_evolution_engine` |
| `interstice_bridge` | Discover and map constellation repository connections | `skills/r1/interstice_bridge` |
| `luminant_memory` | Inspect and organize memory structures while preserving provenance | `skills/r1/luminant_memory` |
| `module_gardener` | Review module lifecycle and propose bounded growth or refactoring | `skills/r1/module_gardener` |
| `oracle_bridge` | Synthesize multi-perspective research and consensus evidence | `skills/r1/oracle_bridge` |
| `paradox_resolver` | Detect module conflicts and propose reviewable resolutions | `skills/r1/paradox_resolver` |
| `pentaxis_integrator` | Plan and validate the Pentaxis 5D engine integration | `skills/r1/pentaxis_integrator` |
| `resonance_mapper` | Map resonance patterns and report bounded trend hypotheses | `skills/r1/resonance_mapper` |
| `reusable_ui_workbench` | Create, edit, preview, verify, and reuse UI components | `skills/r1/reusable_ui_workbench` |
| `season_coordinator` | Coordinate seasonal planning and propose lifecycle changes | `skills/r1/season_coordinator` |
| `skill_builder` | Scaffold, inspect, and propose refactors for reusable skills | `skills/r1/skill_builder` |
| `threshold_engineer` | Analyze transition readiness and propose controlled state changes | `skills/r1/threshold_engineer` |
| `truth_cultivator` | Inspect and challenge beliefs using evidence provenance | `skills/r1/truth_cultivator` |
| `weather_monitor` | Monitor organism vitals and produce bounded health reports | `skills/r1/weather_monitor` |

**Inventory baseline:** 22 repository skill documents. The validator discovers
all `SKILL.md` files recursively, so additions outside this table are detected
and must be registered during review.

## Generation Contract

For generated R1 wave skills, include:
1. YAML frontmatter with non-empty `name` and `description`.
2. `## Capabilities` with the supported `skill:command` entries.
3. `## Roots` with the applicable root/path information.
4. A documented example for each exposed command.
5. A safety section whenever the workflow can mutate state, publish, archive,
   delete, deploy, or contact an external service.

Not every portable skill uses the R1 wave command model. Do not add fake
commands or root tables merely to satisfy a template.

## Wave-Builder Integration

Use `scripts/scaffold_organ.py` for new wave organs and
`scripts/bump_versions.py` to sync VERSION/WAVE across:
`api_server.py`, `api/organism_ontology.py`, `dashboard/shared.js`,
`pyproject.toml`, `CITATION.cff`, and `CHANGELOG.md`.

## Skill Vitality Gate

Every repository `SKILL.md` is checked across the full repository, including
the toolkit extension under `codetools/plugins/`.

Run the static contract and safety scan:

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -p 'test_skill_vitality.py' -v
```

The gate checks required YAML frontmatter, valid and unique names, useful
descriptions, readable non-empty files, likely credential literals, direct
default-branch or production commands, and high-impact action language without
an explicit safety boundary. The latter is reported as a warning. See
[SAFETY.md](SAFETY.md) for the shared execution contract.

A passing static gate is not proof that a skill's external tools, connectors,
provider permissions, or live side effects work. Report static lint, desk
tests, execution tests, integration tests, and production verification
separately.
