---
name: skill-evolution
description: Design, audit, test, refactor, compose, and safely evolve reusable agent skills. Use when creating a new skill, improving an existing skill, consolidating overlapping instructions, validating skill metadata and tool contracts, or building a maintainable skill library.
---

# Skill Evolution

A skill is an executable operating procedure for an agent, not a decorative prompt. Optimize for reliable behavior, clear boundaries, testability, and reuse.

## Operating rules

1. **Inspect before inventing.** Read the repository's skill index, nearby skills, project guidance, tool catalog, and relevant tests. Search for overlap before creating a new skill.
2. **Prefer evolution over duplication.** Extend an existing skill when its purpose and trigger match. Split only when the new workflow has a distinct trigger, inputs, outputs, or safety boundary.
3. **Make instructions operational.** Every major instruction should identify an action, decision rule, expected evidence, or stop condition. Remove vague encouragement and repeated prose.
4. **Treat tool descriptions as contracts.** Use only tools and parameters actually available. Do not invent integrations, permissions, paths, APIs, or execution capabilities.
5. **Use least privilege.** Read first; write only when requested or clearly authorized. Keep destructive, external, financial, production, and irreversible actions behind explicit approval.
6. **Design for partial capability.** State what to do when a connector, file, terminal, credential, or runtime is unavailable. Never fabricate an execution result.
7. **Keep outputs auditable.** Require exact paths, identifiers, revisions, test commands, and outcomes for consequential changes.
8. **Keep the skill portable.** Put project-specific paths and conventions in a clearly marked adapter section, not in the generic core procedure.

## Skill lifecycle

### 1. Discover and classify

Before editing, record:
- the user's intended outcome and recurring trigger;
- candidate skills with overlapping descriptions or workflows;
- repository-specific conventions and supported runtimes;
- tools/connectors actually available;
- expected inputs, outputs, side effects, and approval boundaries.

Choose one outcome:
- **Reuse:** an existing skill already covers the task.
- **Extend:** add a missing procedure to an existing skill.
- **Compose:** call or reference multiple focused skills in a clear sequence.
- **Create:** add a new skill only for a distinct repeatable workflow.
- **Retire:** mark obsolete guidance and provide a migration path; do not silently delete it.

### 2. Write a precise contract

Each skill must define:
- a unique, stable name;
- a concise description that says when to use it;
- scope and explicit non-goals;
- required inputs and assumptions;
- ordered procedure with decision points;
- tool requirements and fallback behavior;
- safety/approval boundaries;
- validation criteria;
- output format and evidence requirements.

Use valid YAML frontmatter. Keep names lowercase and hyphenated. Avoid triggers so broad that the skill fires for unrelated tasks.

### 3. Structure for retrieval

- Put the common workflow first and specialized details in named sections.
- Use checklists only for steps that must be verified, not as decoration.
- Prefer tables for compact contracts and decision matrices.
- Link to shared procedures instead of copying large blocks.
- Keep examples short, realistic, and clearly marked as examples.
- Separate generic guidance from repository adapters and provider-specific instructions.
- Avoid references to unavailable tools or assumed account permissions.

### 4. Validate behavior

For every changed skill:
1. Parse and inspect the frontmatter.
2. Check that the description matches the intended trigger.
3. Check referenced paths, scripts, templates, and tools.
4. Search for contradictory instructions and duplicate rules.
5. Verify that approval gates cover every consequential side effect.
6. Run focused tests or a deterministic fixture where practical.
7. Test at least one normal path, one missing-tool/blocked path, and one unsafe-action path.
8. Review the rendered instructions as a user-facing operating procedure.

A text review is not a runtime test. A passing metadata test does not prove the agent follows the skill correctly. Label each validation layer separately.

### 5. Refine and measure

Use this quality rubric, scoring each dimension 0–2:
- **Trigger precision:** activates for the right work and avoids unrelated tasks.
- **Completeness:** includes inputs, steps, decisions, fallbacks, and outputs.
- **Safety:** explicit authorization, least privilege, and stop conditions.
- **Evidence:** claims and actions are verifiable.
- **Testability:** behavior can be checked with fixtures or concrete acceptance criteria.
- **Maintainability:** low duplication, clear ownership, stable references.

Maximum score: 12. Record the weakest dimension and improve it before adding features. Do not inflate scores without evidence.

### 6. Version and deliver

- Make one coherent skill change per patch.
- Preserve prior behavior unless a breaking change is intentional and documented.
- Update the skill index when adding, renaming, or retiring a skill.
- Add regression fixtures for scripts or machine-readable contracts.
- Use a feature branch and reviewable PR for repository changes.
- Report exact changed paths, revision, validation performed, limitations, and approval status.
- Do not merge, deploy, publish, or mutate production resources unless explicitly authorized.

## Composition patterns

Use the smallest composition that works:

1. **Orchestrator skill:** owns task decomposition, sequencing, and final evidence report.
2. **Specialist skill:** owns one bounded domain such as repository security, HTML sink triage, or deployment verification.
3. **Adapter section:** maps generic steps to a specific provider or repository.
4. **Validation fixture:** tests the specialist's deterministic scripts or metadata contracts.

Avoid circular skill references. The orchestrator may invoke specialists; specialists should not require the orchestrator to complete their core procedure.

## Stop conditions

Stop and report a blocker when:
- the target repository, branch, or artifact is ambiguous;
- required source files cannot be accessed;
- a tool's permissions or side effects are unclear;
- instructions conflict and the conflict changes safety or correctness;
- tests cannot be run and the result would otherwise be presented as verified;
- the proposed change would exceed the user's authorization.

## Delivery report

Use this compact structure:

1. **Decision:** reused, extended, composed, created, or retired.
2. **Changes:** paths and behavior added or changed.
3. **Validation:** metadata, references, tests, fixtures, and manual review, each labelled.
4. **Safety:** side effects performed and approval still required.
5. **Next refinement:** the single weakest quality dimension or highest-value gap.

Do not claim that a skill is installed, registered, discoverable, or executed unless the relevant host/runtime confirms it.
