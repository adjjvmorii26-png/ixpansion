export const WORLD = Object.freeze({width:1000,height:700,cell:50,maxBeacons:24});
export function createWorld(seed=1337){return {tick:0,seed,agent:{id:"agent-0",x:500,y:350,energy:100},beacons:[],nextBeaconId:1,paused:false};}
export function cloneWorld(world){return structuredClone(world);}
export function validateWorld(world){
 const errors=[];
 if(!world||typeof world!=="object"||Array.isArray(world))return ["world must be an object"];
 if(!Number.isSafeInteger(world.tick)||world.tick<0)errors.push("invalid tick");
 if(!Number.isSafeInteger(world.seed)||world.seed<0)errors.push("invalid seed");
 if(!Number.isSafeInteger(world.nextBeaconId)||world.nextBeaconId<1)errors.push("invalid next beacon ID");
 if(typeof world.paused!=="boolean")errors.push("invalid paused flag");
 const a=world.agent;
 if(!a||typeof a!=="object"||typeof a.id!=="string"||!a.id.trim()||!Number.isFinite(a.x)||!Number.isFinite(a.y)||a.x<0||a.x>WORLD.width||a.y<0||a.y>WORLD.height)errors.push("agent out of bounds or invalid ID");
 if(!Number.isFinite(a?.energy)||a.energy<0||a.energy>100)errors.push("energy out of range");
 if(!Array.isArray(world.beacons))errors.push("invalid beacon collection");
 else if(world.beacons.length>WORLD.maxBeacons)errors.push("beacon capacity exceeded");
 const ids=new Set(a&&typeof a.id==="string"?[a.id]:[]);
 if(Array.isArray(world.beacons)){
  for(const b of world.beacons){
   if(!b||typeof b!=="object"){errors.push("invalid beacon");continue;}
   if(typeof b.id!=="string"||!b.id.trim()||ids.has(b.id))errors.push("duplicate or invalid ID");
   if(typeof b.id==="string")ids.add(b.id);
   if(!Number.isFinite(b.x)||!Number.isFinite(b.y)||b.x<0||b.x>WORLD.width||b.y<0||b.y>WORLD.height)errors.push("beacon out of bounds");
   if(!Number.isInteger(b.pulseTicks)||b.pulseTicks<0||b.pulseTicks>10)errors.push("invalid beacon pulse ticks");
  }
 }
 return errors;
}
function canonicalize(value){
 if(Array.isArray(value))return value.map(canonicalize);
 if(value&&typeof value==="object")return Object.keys(value).sort().reduce((out,key)=>{out[key]=canonicalize(value[key]);return out;},{});
 return value;
}
// FNV-1a is a compact consistency fingerprint, not a cryptographic integrity proof.
export function hashWorld(world){
 const input=JSON.stringify(canonicalize(world));let h=0x811c9dc5;
 for(let i=0;i<input.length;i++){h^=input.charCodeAt(i);h=Math.imul(h,0x01000193);}
 return (h>>>0).toString(16).padStart(8,"0");
}
function reject(reason){return {accepted:false,reason};}
export function transition(current,action){
 if(validateWorld(current).length)return reject("source state is invalid");
 if(!action||typeof action.type!=="string")return reject("invalid action");
 const next=cloneWorld(current);
 if(next.paused&&action.type!=="step"&&action.type!=="pause")return reject("world is paused");
 const spend=n=>{if(next.agent.energy<n)return false;next.agent.energy-=n;return true;};
 switch(action.type){
  case "pause": next.paused=!next.paused;break;
  case "step": if(!next.paused)return reject("pause before stepping");break;
  case "move":{
   const dx=Number(action.dx),dy=Number(action.dy);
   if(!Number.isFinite(dx)||!Number.isFinite(dy)||Math.hypot(dx,dy)>WORLD.cell)return reject("movement delta exceeds one cell");
   const x=next.agent.x+dx,y=next.agent.y+dy;
   if(x<0||x>WORLD.width||y<0||y>WORLD.height)return reject("world boundary");
   if(next.beacons.some(b=>Math.hypot(b.x-x,b.y-y)<22))return reject("beacon collision");
   if(!spend(1))return reject("no energy");
   next.agent.x=x;next.agent.y=y;break;
  }
  case "place":{
   const x=Number(action.x),y=Number(action.y);
   if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>WORLD.width||y<0||y>WORLD.height)return reject("placement out of bounds");
   if(next.beacons.length>=WORLD.maxBeacons)return reject("beacon capacity reached");
   if(Math.hypot(next.agent.x-x,next.agent.y-y)<24||next.beacons.some(b=>Math.hypot(b.x-x,b.y-y)<24))return reject("collision");
   if(!spend(3))return reject("no energy");
   next.beacons.push({id:"beacon-"+next.nextBeaconId++,x,y,pulseTicks:0});break;
  }
  case "remove":{
   const x=Number(action.x),y=Number(action.y);if(!Number.isFinite(x)||!Number.isFinite(y))return reject("invalid removal point");
   let index=-1,distance=Infinity;
   next.beacons.forEach((b,i)=>{const d=Math.hypot(b.x-x,b.y-y);if(d<distance){distance=d;index=i;}});
   if(index<0||distance>75)return reject("no beacon in range");
   next.beacons.splice(index,1);break;
  }
  case "recharge": next.agent.energy=Math.min(100,next.agent.energy+20);break;
  case "pulse": if(!spend(2))return reject("no energy");next.beacons.forEach(b=>b.pulseTicks=10);break;
  default:return reject("unknown action: "+action.type);
 }
 if(action.type!=="pause"){for(const b of next.beacons)b.pulseTicks=Math.max(0,b.pulseTicks-1);next.tick++;}
 const errors=validateWorld(next);if(errors.length)return reject(errors.join(", "));
 return {accepted:true,world:next,hash:hashWorld(next)};
}
