/**
 * Short automated fitness probe for motion-evolution
 * Runs a fixed-horizon simulation offline (no DOM) and returns scores.
 */

function createProbeWorld(genome) {
  const rules = {
    gravity: 0.06, friction: 0.99, restitution: 0.8, maxSpeed: 16, substeps: 2, wallRestitution: 0.65,
    ...(genome.physics || {})
  };
  const thrust = genome.controller?.thrustStrength ?? 1.2;
  const playerMass = genome.controller?.playerMass ?? 2.0;
  const W = 720, H = 480;
  const entities = [
    { id: 'player', x: 360, y: 240, vx: 0, vy: 0, r: 14, mass: playerMass, dynamic: true },
    { id: 'b1', x: 200, y: 160, vx: 2.2, vy: 1.1, r: 15, mass: 1, dynamic: true },
    { id: 'b2', x: 520, y: 300, vx: -1.6, vy: -1.8, r: 12, mass: 0.85, dynamic: true },
    { id: 'b3', x: 340, y: 100, vx: 0.4, vy: 2.6, r: 10, mass: 0.65, dynamic: true }
  ];
  return { rules, thrust, entities, W, H, t: 0, collisions: 0, maxSpeedSeen: 0, energySamples: [], posSamples: [] };
}

function stepWorld(world, action) {
  const { rules, entities, W, H } = world;
  const sub = rules.substeps || 2;
  const g = rules.gravity, fr = rules.friction, maxSp = rules.maxSpeed, wr = rules.wallRestitution;
  if (action && action.type === 'thrust') {
    const p = entities.find(e => e.id === 'player');
    if (p) { p.vx += (action.payload?.dx || 0) * world.thrust; p.vy += (action.payload?.dy || 0) * world.thrust; }
  }
  for (let s = 0; s < sub; s++) {
    for (const e of entities) {
      if (!e.dynamic) continue;
      e.vy += g / sub; e.vx *= Math.pow(fr, 1/sub); e.vy *= Math.pow(fr, 1/sub);
      e.x += e.vx / sub; e.y += e.vy / sub;
    }
    for (let i = 0; i < entities.length; i++) {
      for (let j = i+1; j < entities.length; j++) {
        const a = entities[i], b = entities[j];
        const dx = b.x-a.x, dy = b.y-a.y;
        const dist = Math.hypot(dx,dy)||0.0001;
        const minDist = a.r+b.r;
        if (dist >= minDist) continue;
        world.collisions++;
        const nx=dx/dist, ny=dy/dist, overlap=minDist-dist;
        const invA=1/a.mass, invB=1/b.mass, totalInv=invA+invB;
        const corr=overlap*0.82;
        a.x-=nx*corr*(invA/totalInv); a.y-=ny*corr*(invA/totalInv);
        b.x+=nx*corr*(invB/totalInv); b.y+=ny*corr*(invB/totalInv);
        const rvx=b.vx-a.vx, rvy=b.vy-a.vy, velN=rvx*nx+rvy*ny;
        if (velN>0) continue;
        const jImp=-(1+rules.restitution)*velN/totalInv;
        a.vx-=jImp*nx*invA; a.vy-=jImp*ny*invA;
        b.vx+=jImp*nx*invB; b.vy+=jImp*ny*invB;
      }
    }
    for (const e of entities) {
      if (e.x<e.r){e.x=e.r;e.vx*=-wr;} if (e.x>W-e.r){e.x=W-e.r;e.vx*=-wr;}
      if (e.y<e.r){e.y=e.r;e.vy*=-wr;} if (e.y>H-e.r){e.y=H-e.r;e.vy*=-wr;}
      const sp=Math.hypot(e.vx,e.vy);
      if (sp>maxSp){e.vx*=maxSp/sp;e.vy*=maxSp/sp;}
      if (sp>world.maxSpeedSeen) world.maxSpeedSeen=sp;
    }
  }
  world.t += 1;
}

function runFitnessProbe(genome, opts={}) {
  const horizon = opts.horizon || 400;
  const world = createProbeWorld(genome);
  const sequence = [];
  for (let t=0; t<horizon; t++) {
    const phase=(t%120)/120;
    let dx=0,dy=0;
    if (phase<0.25) dx=1; else if (phase<0.5) dy=-1; else if (phase<0.75) dx=-1; else dy=1;
    sequence.push(t%4===0 ? {type:'thrust', payload:{dx,dy}} : null);
  }
  let totalKE=0, totalJerk=0, prevVx=0, prevVy=0;
  const player=()=>world.entities.find(e=>e.id==='player');
  for (let t=0; t<horizon; t++) {
    const p=player();
    stepWorld(world, sequence[t]);
    const ke=world.entities.reduce((s,e)=>s+0.5*e.mass*(e.vx*e.vx+e.vy*e.vy),0);
    totalKE+=ke;
    const jerk=Math.hypot(p.vx-prevVx, p.vy-prevVy);
    totalJerk+=jerk; prevVx=p.vx; prevVy=p.vy;
    world.posSamples.push({x:p.x,y:p.y});
  }
  const avgKE=totalKE/horizon, avgJerk=totalJerk/horizon, collisionRate=world.collisions/horizon;
  const stability=Math.max(0,1-Math.max(0,world.maxSpeedSeen-14)/10)*Math.max(0,1-collisionRate*2);
  const energy=Math.max(0,1-Math.abs(avgKE-8)/20);
  const smoothness=Math.max(0,1-avgJerk/3);
  const xs=world.posSamples.map(p=>p.x), ys=world.posSamples.map(p=>p.y);
  const controllability=Math.min(1,(Math.max(...xs)-Math.min(...xs)+Math.max(...ys)-Math.min(...ys))/500);
  const interest=Math.min(1,0.4+collisionRate*3+(world.maxSpeedSeen/20));
  const aggregate=stability*0.3+energy*0.2+smoothness*0.2+controllability*0.2+interest*0.1;
  return {
    genomeId: genome.id||'unknown', horizon,
    scores: { stability:+stability.toFixed(3), energy:+energy.toFixed(3), smoothness:+smoothness.toFixed(3), controllability:+controllability.toFixed(3), interest:+interest.toFixed(3) },
    aggregate:+aggregate.toFixed(3),
    raw: { collisions:world.collisions, maxSpeedSeen:+world.maxSpeedSeen.toFixed(2), avgKE:+avgKE.toFixed(2), avgJerk:+avgJerk.toFixed(3) }
  };
}

if (typeof module!=='undefined') module.exports={runFitnessProbe};
if (typeof window!=='undefined') window.runFitnessProbe=runFitnessProbe;
