/** Maps internal skill metadata to contextual user-facing capabilities. */
export function discoverSkills(registry, context = {}) {
  const active = new Set(Array.isArray(context.tags) ? context.tags : []);
  if (typeof context.surface === "string") active.add(context.surface);
  return registry.list()
    .filter(skill => skill.contexts.some(tag => active.has(tag)))
    .map(({ id, version, label, description, capabilities }) => ({ id, version, label, description, capabilities: [...capabilities] }));
}
