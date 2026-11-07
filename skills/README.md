# Skill Library

Reusable operating procedures maintained in this repository.

## Core engineering

| Skill | Trigger | Role |
|---|---|---|
| [verified-repo-refinement](verified-repo-refinement/SKILL.md) | Repository audits, security/reliability triage, focused fixes, regression tests, CI evidence | Audits and refines code with traceable evidence and safe PR delivery |
| [skill-evolution](skill-evolution/SKILL.md) | Creating, reviewing, composing, testing, or maintaining reusable skills | Governs the skill lifecycle, quality checks, and library consistency |
| [reusable-ui-workbench](r1/reusable_ui_workbench/SKILL.md) | Building, editing, testing, or reusing UI components and design systems | Composes and maintains portable UI assets |

## Maintenance rules

- Search this index and recursively inspect `skills/**/SKILL.md` before creating another skill.
- Treat the index as the human-readable routing map; every discovered skill must have one accurate entry pointing to its actual path.
- Prefer extending or composing an existing skill over duplicating instructions.
- Keep each skill's frontmatter name unique and its description trigger-specific.
- Update this index when adding, renaming, or retiring a skill.
- Test scripts and machine-readable contracts; distinguish those tests from manual instruction review.
- Keep provider-specific procedures separate from generic skill logic.
- Never claim a skill is available in a host runtime until that runtime confirms discovery.
