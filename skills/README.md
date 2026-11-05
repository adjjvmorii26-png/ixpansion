# Skill Library

Reusable operating procedures maintained in this repository.

## Core engineering

| Skill | Trigger | Role |
|---|---|---|
| [verified-repo-refinement](verified-repo-refinement/SKILL.md) | Repository audits, security/reliability triage, focused fixes, regression tests, CI evidence | Audits and refines code with traceable evidence and safe PR delivery |
| [skill-evolution](skill-evolution/SKILL.md) | Creating, reviewing, composing, testing, or maintaining reusable skills | Governs the skill lifecycle, quality checks, and library consistency |

## Maintenance rules

- Search this index and existing skill directories before creating another skill.
- Prefer extending or composing an existing skill over duplicating instructions.
- Keep each skill's frontmatter name unique and its description trigger-specific.
- Update this index when adding, renaming, or retiring a skill.
- Test scripts and machine-readable contracts; distinguish those tests from manual instruction review.
- Keep provider-specific procedures separate from generic skill logic.
- Never claim a skill is available in a host runtime until that runtime confirms discovery.
