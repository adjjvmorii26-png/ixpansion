# Deep Skill Embedding v0.1

Skills live inside the feature module that owns their context. The user sees a small contextual action surface; registry, routing, policy, and evidence plumbing stay internal.

## Flow

`selection/context → discoverSkills() → approval gate → SkillRuntime → evidence envelope`

- Manifests are declarative metadata, not executable code.
- Runtime adapters are explicitly supplied by trusted host code. No eval, import-from-manifest, or arbitrary code loading.
- Capability grants are checked before execution.
- Approval is required by default; dry-run returns a pending result.
- Input/output payloads, execution time, and nesting depth are bounded.
- Dependency graphs are checked for missing nodes and cycles.
- Evidence records preserve source mode and start as PENDING. This bridge does not sign or independently verify evidence.

## Important boundary

The timeout bounds how long the caller waits, but cannot forcibly stop an adapter that ignores cancellation. This is a trusted-adapter dispatcher, **not** a process or browser security sandbox. Untrusted skills require worker/process isolation and enforceable cancellation before production use.

## Example

```js
import { SkillRegistry } from "./skill_registry.mjs";
import { discoverSkills } from "./skill_router.mjs";
import { SkillRuntime } from "./skill_runtime.mjs";
import { createSkillEvidence } from "./evidence_bridge.mjs";

const registry = new SkillRegistry();
registry.register({
  id: "holodeck.spatial-inspector", version: "0.1.0",
  label: "Inspect object", description: "Summarizes selected object state.",
  contexts: ["object.selected"], capabilities: ["spatial.read"],
  input: { type: "object" }, output: { type: "object" },
  limits: { timeoutMs: 500, maxInputBytes: 4096, maxDepth: 1 }
});
const adapters = new Map([["holodeck.spatial-inspector", async ({ object }) => ({
  position: object.position, radius: object.radius
})]]);
const visibleActions = discoverSkills(registry, { tags: ["object.selected"] });
const runtime = new SkillRuntime({ registry, adapters });
const result = await runtime.execute("holodeck.spatial-inspector", { object: selectedObject }, {
  grantedCapabilities: ["spatial.read"], approved: true
});
const evidence = createSkillEvidence({ skill: registry.get("holodeck.spatial-inspector"), result });
```

## Test

`node --test holodeck/skills/skill_runtime.test.mjs`
