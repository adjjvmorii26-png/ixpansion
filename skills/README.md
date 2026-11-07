# Skill Library

Reusable operating procedures maintained in this repository.

## Core engineering

| Skill | Trigger | Role |
|---|---|---|
| [verified-repo-refinement](verified-repo-refinement/SKILL.md) | Repository audits, security/reliability triage, focused fixes, regression tests, CI evidence | Audits and refines code with traceable evidence and safe PR delivery |
| [skill-evolution](skill-evolution/SKILL.md) | Creating, reviewing, composing, testing, or maintaining reusable skills | Governs the skill lifecycle, quality checks, and library consistency |
| [reusable-ui-workbench](r1/reusable_ui_workbench/SKILL.md) | Building, editing, testing, or reusing UI components and design systems | Composes and maintains portable UI assets |

## Project organism (R1 collection)

These existing specialist skills are retained in their original paths and naming convention. Their detailed triggers and procedures live in each definition.

| Skill | Definition | Trigger summary |
|---|---|---|
| `antimemetic_weave` | [Open](r1/antimemetic_weave/SKILL.md) | See skill definition |
| `blog_curator` | [Open](r1/blog_curator/SKILL.md) | See skill definition |
| `chrono_relay` | [Open](r1/chrono_relay/SKILL.md) | See skill definition |
| `data_pipeline_asynchronous_engine` | [Open](r1/data_pipeline_asynchronous_engine/SKILL.md) | See skill definition |
| `dream_compiler` | [Open](r1/dream_compiler/SKILL.md) | See skill definition |
| `handler_handler_engine` | [Open](r1/handler_handler_engine/SKILL.md) | See skill definition |
| `handler_meta_evolution_engine` | [Open](r1/handler_meta_evolution_engine/SKILL.md) | See skill definition |
| `interstice_bridge` | [Open](r1/interstice_bridge/SKILL.md) | See skill definition |
| `luminant_memory` | [Open](r1/luminant_memory/SKILL.md) | See skill definition |
| `module_gardener` | [Open](r1/module_gardener/SKILL.md) | See skill definition |
| `oracle_bridge` | [Open](r1/oracle_bridge/SKILL.md) | See skill definition |
| `paradox_resolver` | [Open](r1/paradox_resolver/SKILL.md) | See skill definition |
| `pentaxis_integrator` | [Open](r1/pentaxis_integrator/SKILL.md) | See skill definition |
| `resonance_mapper` | [Open](r1/resonance_mapper/SKILL.md) | See skill definition |
| `season_coordinator` | [Open](r1/season_coordinator/SKILL.md) | See skill definition |
| `skill_builder` | [Open](r1/skill_builder/SKILL.md) | See skill definition |
| `threshold_engineer` | [Open](r1/threshold_engineer/SKILL.md) | See skill definition |
| `truth_cultivator` | [Open](r1/truth_cultivator/SKILL.md) | See skill definition |
| `weather_monitor` | [Open](r1/weather_monitor/SKILL.md) | See skill definition |

## Toolkit extension

| Skill | Definition | Trigger summary |
|---|---|---|
| `ixpansion-wave-builder` | [Open](../codetools/plugins/ixpansion-toolkit/skills/ixpansion-wave-builder/SKILL.md) | Scaffold and wire IXPANSION API evolution waves |

## Maintenance rules

- Search this index and recursively inspect `skills/**/SKILL.md` before creating another skill.
- Treat the index as the human-readable routing map; every discovered skill must have one accurate entry pointing to its actual path.
- Prefer extending or composing an existing skill over duplicating instructions.
- Keep each skill's frontmatter name unique and its description trigger-specific.
- Update this index when adding, renaming, or retiring a skill.
- Test scripts and machine-readable contracts; distinguish those tests from manual instruction review.
- Keep provider-specific procedures separate from generic skill logic.
- Never claim a skill is available in a host runtime until that runtime confirms discovery.
