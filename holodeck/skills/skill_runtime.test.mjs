import test from "node:test";
import assert from "node:assert/strict";
import { SkillRegistry } from "./skill_registry.mjs";
import { discoverSkills } from "./skill_router.mjs";
import { SkillRuntime } from "./skill_runtime.mjs";
import { createSkillEvidence } from "./evidence_bridge.mjs";

const manifest = (overrides={}) => ({
 id:"holodeck.spatial-inspector", version:"0.1.0", label:"Inspect object",
 description:"Summarizes selected object state.", contexts:["object.selected"],
 capabilities:["spatial.read"], input:{type:"object"}, output:{type:"object"},
 limits:{timeoutMs:100,maxInputBytes:1024,maxDepth:1}, ...overrides
});
test("contextual discovery surfaces only matching skills",()=>{
 const registry=new SkillRegistry(); registry.register(manifest());
 assert.equal(discoverSkills(registry,{tags:["object.selected"]}).length,1);
 assert.equal(discoverSkills(registry,{tags:["timeline.selected"]}).length,0);
});
test("registry rejects invalid capability and dependency cycles",()=>{
 const registry=new SkillRegistry();
 assert.throws(()=>registry.register(manifest({capabilities:["filesystem.root"]})),/capabilities/);
 registry.register(manifest({id:"skill.alpha",dependencies:["skill.beta"]}));
 assert.throws(()=>registry.register(manifest({id:"skill.beta",dependencies:["skill.alpha"]})),/cycle/);
});
test("execution requires grants and explicit approval",async()=>{
 const registry=new SkillRegistry(); registry.register(manifest());
 const runtime=new SkillRuntime({registry,adapters:new Map([["holodeck.spatial-inspector",async x=>({id:x.id})]])});
 await assert.rejects(runtime.execute("holodeck.spatial-inspector",{id:7},{approved:true}),/capability not granted/);
 const pending=await runtime.execute("holodeck.spatial-inspector",{id:7},{grantedCapabilities:["spatial.read"]});
 assert.equal(pending.status,"PENDING");
 const done=await runtime.execute("holodeck.spatial-inspector",{id:7},{grantedCapabilities:["spatial.read"],approved:true});
 assert.deepEqual(done.output,{id:7});
});
test("runtime bounds input and nesting",async()=>{
 const registry=new SkillRegistry(); registry.register(manifest());
 const runtime=new SkillRuntime({registry,adapters:new Map([["holodeck.spatial-inspector",async x=>x]]),maxInputBytes:32});
 await assert.rejects(runtime.execute("holodeck.spatial-inspector",{payload:"x".repeat(100)},{approved:true,grantedCapabilities:["spatial.read"]}),/byte limit/);
 await assert.rejects(runtime.execute("holodeck.spatial-inspector",{}, {approved:true,grantedCapabilities:["spatial.read"],depth:2}),/depth/);
});
test("evidence preserves simulated source and pending verification state",()=>{
 const result={status:"COMPLETED",output:{position:[1,2,3]}};
 const envelope=createSkillEvidence({skill:manifest(),result,context:{mode:"SIMULATED"},now:()=>1000});
 assert.equal(envelope.source.mode,"SIMULATED");
 assert.equal(envelope.source.evidenceStatus,"PENDING");
 assert.deepEqual(envelope.output,{position:[1,2,3]});
});
