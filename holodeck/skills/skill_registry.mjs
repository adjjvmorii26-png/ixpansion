const ID = /^[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const ALLOWED = new Set(["spatial.read","spatial.annotate","physics.read","evidence.write"]);
const clone = value => structuredClone(value);
function validate(m) {
 if (!m || typeof m !== "object" || Array.isArray(m)) throw new TypeError("manifest must be an object");
 for (const k of ["id","version","label","description","contexts","capabilities","input","output"]) if (!(k in m)) throw new TypeError("manifest missing " + k);
 if (!ID.test(m.id) || !/^\d+\.\d+\.\d+$/.test(m.version)) throw new TypeError("invalid id or version");
 if (typeof m.label !== "string" || !m.label.trim() || m.label.length > 64) throw new TypeError("invalid label");
 if (typeof m.description !== "string" || !m.description.trim() || m.description.length > 500) throw new TypeError("invalid description");
 if (!Array.isArray(m.contexts) || !m.contexts.length || m.contexts.some(x => typeof x !== "string" || !x || x.length > 64)) throw new TypeError("invalid contexts");
 if (!Array.isArray(m.capabilities) || m.capabilities.some(x => !ALLOWED.has(x)) || new Set(m.capabilities).size !== m.capabilities.length) throw new TypeError("invalid capabilities");
 if (m.dependencies != null && (!Array.isArray(m.dependencies) || m.dependencies.some(x => typeof x !== "string" || !ID.test(x)))) throw new TypeError("invalid dependencies");
 const l=m.limits ?? {};
 if (l.timeoutMs != null && (!Number.isInteger(l.timeoutMs)||l.timeoutMs<1||l.timeoutMs>5000)) throw new RangeError("invalid timeoutMs");
 if (l.maxInputBytes != null && (!Number.isInteger(l.maxInputBytes)||l.maxInputBytes<1||l.maxInputBytes>65536)) throw new RangeError("invalid maxInputBytes");
 if (l.maxDepth != null && (!Number.isInteger(l.maxDepth)||l.maxDepth<0||l.maxDepth>4)) throw new RangeError("invalid maxDepth");
 return clone(m);
}
export class SkillRegistry {
 #skills = new Map();
 register(manifest) {
  const m=validate(manifest);
  if(this.#skills.has(m.id)) throw new Error("duplicate skill: "+m.id);
  this.#skills.set(m.id,m);
  try { this.#assertGraph(); } catch(e) { this.#skills.delete(m.id); throw e; }
  return m.id;
 }
 #assertGraph() {
  const active=new Set(), done=new Set();
  const visit=id=>{ if(active.has(id)) throw new Error("skill dependency cycle"); if(done.has(id)) return; const m=this.#skills.get(id); if(!m) throw new Error("missing skill dependency: "+id); active.add(id); for(const dep of m.dependencies??[]) visit(dep); active.delete(id); done.add(id); };
  for(const id of this.#skills.keys()) visit(id);
 }
 get(id) { const m=this.#skills.get(id); return m ? clone(m) : null; }
 list() { return [...this.#skills.values()].map(clone); }
}
