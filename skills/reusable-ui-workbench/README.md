# Reusable UI Workbench

A framework-aware workflow for creating, editing, composing, previewing, cataloging, verifying, and reusing UI components across IXPANSION and compatible projects.

## Quick start
1. Read [SKILL.md](SKILL.md).
2. Inspect the current component and its consumers before editing.
3. Copy [the component contract](templates/component-contract.md) for components intended for reuse.
4. Use [the registry example](examples/component-registry.json) as a lightweight catalog shape; replace the sample with real components before treating it as an inventory.
5. Use the skill workflows: `ui:discover`, `ui:contract`, `ui:edit`, `ui:compose`, `ui:preview`, `ui:verify`, `ui:catalog`, `ui:extract`, and `ui:migrate`.
6. Run relevant repository checks and report actual results.

## Suggested component lifecycle
**Draft → Contracted → Implemented → Previewed → Verified → Cataloged → Reused**

A component must not be labeled verified unless its documented checks have actually run. A preview or deployment alone does not prove accessibility or behavior. Reuse should point to a source of truth or record provenance when copied.

## Practical guardrails
- Reuse existing primitives before adding dependencies or duplicate components.
- Keep generic presentation components free of app-specific domain logic.
- Record actual verification status, not intended status.
- Test in the destination project when porting a component across repositories.
