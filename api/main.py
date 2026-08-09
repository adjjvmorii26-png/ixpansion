import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent import Agent
from aether_lattice import AetherLattice
from lattice_stack import LatticePolicy, Machine, MachineLattice
from security_controls import URLPolicy
from web_resources import PublicResourceCollector

app = FastAPI(title="IXPANSION API", version="1.2.0-rc3")
foundation = AetherLattice(
    agent=Agent(name="aether-agent"),
    lattice=MachineLattice(
        [
            Machine("api-healthy-0", health=0.95, capacity=0.8),
            Machine("api-reuse-0", health=0.55, capacity=0.35),
        ],
        policy=LatticePolicy(heartbeat_timeout=300),
    ),
)
agent = foundation.agent
lattice = foundation.lattice
resource_collector = PublicResourceCollector(
    URLPolicy(
        host.strip()
        for host in os.getenv("IXPANSION_RESOURCE_HOSTS", "").split(",")
        if host.strip()
    )
)


class SkillRequest(BaseModel):
    text: str = ""


class HeartbeatRequest(BaseModel):
    machine_id: str
    health: Optional[float] = None
    capacity: Optional[float] = None
    trust: Optional[float] = None
    load: Optional[float] = None


class AllocationRequest(BaseModel):
    task: str
    critical: bool = False
    lease_seconds: Optional[float] = None


class AetherDispatchRequest(AllocationRequest):
    operator: str = "aether"
    task_id: Optional[str] = None


class WorkflowRequest(BaseModel):
    text: str
    critical: bool = False
    lease_seconds: Optional[float] = None
    operator: str = "aether"
    task_id: Optional[str] = None


class ReusableDataRequest(BaseModel):
    value: object


class RecycleRequest(BaseModel):
    text: str
    chunk_size: int = 800
    task_id: Optional[str] = None


class ContextRetrieveRequest(BaseModel):
    query: str = ""
    max_tokens: int = 800


class ResourceRequest(BaseModel):
    url: str
    chunk_size: int = 800
    task_id: Optional[str] = None


@app.get("/")
def read_root() -> dict:
    return {"service": "ixpansion", "status": "ok"}


@app.get("/aether")
def aether_status() -> dict:
    return foundation.snapshot()


@app.post("/aether/dispatch")
def aether_dispatch(request: AetherDispatchRequest) -> dict:
    try:
        return foundation.dispatch(
            request.task,
            critical=request.critical,
            lease_seconds=request.lease_seconds,
            operator=request.operator,
            task_id=request.task_id,
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/aether/workflows")
def aether_workflows() -> dict:
    return {"workflows": foundation.workflows()}


@app.post("/aether/workflows/{workflow}")
def aether_workflow(workflow: str, request: WorkflowRequest) -> dict:
    try:
        return foundation.run_workflow(
            workflow,
            request.text,
            critical=request.critical,
            lease_seconds=request.lease_seconds,
            operator=request.operator,
            task_id=request.task_id,
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/aether/data")
def aether_data_keys() -> dict:
    return {"keys": foundation.list_data()}


@app.get("/aether/data/{key}")
def aether_data_get(key: str) -> dict:
    try:
        return {"key": key, "value": foundation.load_data(key)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/aether/data/{key}")
def aether_data_put(key: str, request: ReusableDataRequest) -> dict:
    try:
        return foundation.save_data(key, request.value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/aether/recycle")
def aether_recycle(request: RecycleRequest) -> dict:
    try:
        return foundation.recycle_data(
            request.text,
            chunk_size=request.chunk_size,
            task_id=request.task_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/aether/context/{key}/retrieve")
def aether_context_retrieve(key: str, request: ContextRetrieveRequest) -> dict:
    try:
        return foundation.retrieve_context(
            key,
            query=request.query,
            max_tokens=request.max_tokens,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
        return """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>IXPANSION / Control Room</title>
    <style>
        :root { --ink: #17211b; --muted: #66736a; --paper: #f4f1e8; --panel: #fffdf7; --line: #d8d7c9; --green: #23734e; --lime: #d8f36a; --orange: #e87941; }
        * { box-sizing: border-box; }
        body { margin: 0; color: var(--ink); background: radial-gradient(circle at 85% 0%, #e3edb2 0, transparent 32%), var(--paper); font: 16px/1.45 Georgia, serif; }
        main { max-width: 1180px; margin: 0 auto; padding: 36px 22px 56px; }
        header { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 30px; }
        h1, h2, p { margin: 0; } h1 { font: 700 clamp(2.4rem, 7vw, 5.8rem)/.9 Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif; letter-spacing: .02em; text-transform: uppercase; }
        h2 { font: 700 1.15rem/1.1 "Arial Narrow", Arial, sans-serif; letter-spacing: .08em; text-transform: uppercase; }
        .eyebrow { color: var(--green); font: 700 .75rem/1.2 "Arial Narrow", Arial, sans-serif; letter-spacing: .16em; text-transform: uppercase; margin-bottom: 10px; }
        .status { display: flex; align-items: center; gap: 9px; color: var(--muted); font: 700 .8rem "Arial Narrow", Arial, sans-serif; text-transform: uppercase; }
        .dot { width: 11px; height: 11px; border-radius: 50%; background: var(--orange); } .dot.live { background: var(--green); box-shadow: 0 0 0 5px #23734e22; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
        .panel { background: color-mix(in srgb, var(--panel) 88%, transparent); border: 1px solid var(--line); padding: 22px; box-shadow: 5px 5px 0 #17211b12; }
        .overview { grid-column: span 4; min-height: 170px; } .overview strong { display: block; margin-top: 15px; font: 700 3rem/1 Impact, sans-serif; color: var(--green); }
        .machines { grid-column: span 8; } .skills { grid-column: span 7; } .actions { grid-column: span 5; }
        .panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 13px; margin-bottom: 14px; }
        .machine { display: grid; grid-template-columns: 1fr auto; gap: 5px 12px; padding: 12px 0; border-bottom: 1px solid var(--line); } .machine:last-child { border-bottom: 0; }
        .machine-name { font: 700 1.1rem "Arial Narrow", Arial, sans-serif; } .machine-meta, .hint { color: var(--muted); font-size: .9rem; }
        .badge { align-self: center; padding: 4px 9px; background: var(--lime); color: var(--ink); font: 700 .7rem "Arial Narrow", Arial, sans-serif; text-transform: uppercase; }
        .skill-list { display: flex; flex-wrap: wrap; gap: 8px; } .skill { padding: 7px 10px; border: 1px solid var(--line); font: 700 .8rem "Arial Narrow", Arial, sans-serif; }
        .workflow-panel { grid-column: 1 / -1; background: var(--ink); color: var(--panel); }
        .workflow-panel .panel-head { border-color: #ffffff2b; }
        .workflow-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .workflow-card { display: grid; gap: 12px; min-height: 145px; padding: 15px; border: 1px solid #ffffff2b; background: #24342b; }
        .workflow-card h3 { margin: 0; color: var(--lime); font: 700 1rem "Arial Narrow", Arial, sans-serif; letter-spacing: .04em; text-transform: uppercase; }
        .workflow-card p { color: #d4ddd5; font-size: .88rem; }
        .workflow-card button { align-self: end; justify-self: start; padding: 8px 10px; background: var(--lime); color: var(--ink); }
        .workflow-card button:hover { background: #efffb1; }
        .workflow-output { grid-column: 1 / -1; min-height: 25px; color: var(--lime); font-size: .9rem; white-space: pre-wrap; }
        form { display: grid; gap: 11px; } label { font: 700 .78rem "Arial Narrow", Arial, sans-serif; text-transform: uppercase; letter-spacing: .07em; }
        input { width: 100%; padding: 11px 12px; border: 1px solid var(--line); background: #fff; color: var(--ink); font: 1rem Georgia, serif; } button { cursor: pointer; border: 0; padding: 12px 15px; background: var(--green); color: #fff; font: 700 .85rem "Arial Narrow", Arial, sans-serif; letter-spacing: .06em; text-transform: uppercase; } button:hover { background: #18583c; }
        #message { min-height: 22px; color: var(--green); font-size: .9rem; } footer { margin-top: 24px; color: var(--muted); font: .8rem "Arial Narrow", Arial, sans-serif; }
        @media (max-width: 760px) { header { display: block; } .status { margin-top: 18px; } .overview, .machines, .skills, .actions { grid-column: 1 / -1; } .workflow-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <main>
        <header><div><p class="eyebrow">Local operations view / 01</p><h1>Control<br>Room</h1></div><div class="status"><span id="health-dot" class="dot"></span><span id="health-text">Connecting</span></div></header>
        <section class="grid">
            <article class="panel overview"><h2>System pulse</h2><strong id="machine-count">--</strong><p class="hint">machines reporting in the lattice</p></article>
            <article class="panel overview"><h2>Local skills</h2><strong id="skill-count">--</strong><p class="hint">offline capabilities available</p></article>
            <article class="panel overview"><h2>Refresh</h2><strong id="refresh-count">--</strong><p class="hint">seconds until the next sync</p></article>
            <article class="panel machines"><div class="panel-head"><h2>Lattice telemetry</h2><span class="hint" id="updated">Waiting for data</span></div><div id="machines"><p class="hint">Loading machine states...</p></div></article>
            <article class="panel skills"><div class="panel-head"><h2>Agent skills</h2><span class="hint">ready offline</span></div><div id="skills" class="skill-list"></div></article>
            <article class="panel actions"><div class="panel-head"><h2>Allocate work</h2></div><form id="allocate-form"><label for="task">Task description</label><input id="task" name="task" placeholder="e.g. inspect the API" required><button type="submit">Request a machine</button><p id="message" role="status"></p></form></article>
            <article class="panel workflow-panel"><div class="panel-head"><h2>Automation workflows</h2><span>offline / one click</span></div><div id="workflows" class="workflow-grid"><p>Loading workflows...</p></div><p id="workflow-output" class="workflow-output" role="status"></p></article>
        </section>
        <footer>IXPANSION local dashboard · data refreshes every 10 seconds · <a href="/docs">API docs</a></footer>
    </main>
    <script>
        const $ = (id) => document.getElementById(id);
        let countdown = 10;
        async function refresh() {
            try {
                const [health, lattice, skillData, workflowData] = await Promise.all([fetch('/health'), fetch('/lattice'), fetch('/skills'), fetch('/aether/workflows')]);
                if (!health.ok || !lattice.ok || !skillData.ok || !workflowData.ok) throw new Error('API unavailable');
                const latticeJson = await lattice.json(); const skillsJson = await skillData.json(); const workflowsJson = await workflowData.json();
                const machines = Object.entries(latticeJson.states || {});
                $('health-dot').classList.add('live'); $('health-text').textContent = 'System healthy';
                $('machine-count').textContent = machines.length; $('skill-count').textContent = skillsJson.skills.length;
                $('machines').innerHTML = machines.map(([name, state]) => `<div class="machine"><div><div class="machine-name">${name}</div><div class="machine-meta">${state}</div></div><span class="badge">${state}</span></div>`).join('') || '<p class="hint">No machines registered.</p>';
                $('skills').innerHTML = skillsJson.skills.map((skill) => `<span class="skill">${skill.name}</span>`).join('');
                $('workflows').innerHTML = workflowsJson.workflows.map((workflow) => `<div class="workflow-card"><h3>${workflow.name}</h3><p>${workflow.description}</p><button type="button" data-workflow="${workflow.name}">Run workflow</button></div>`).join('');
                $('updated').textContent = `Updated ${new Date().toLocaleTimeString()}`; countdown = 10;
            } catch (error) { $('health-text').textContent = 'API unavailable'; $('message').textContent = error.message; }
        }
        $('allocate-form').addEventListener('submit', async (event) => { event.preventDefault(); $('message').textContent = 'Requesting...'; const response = await fetch('/lattice/allocate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({task: $('task').value}) }); const data = await response.json(); $('message').textContent = response.ok ? `Assigned to ${data.machine_id}` : data.detail; if (response.ok) { $('task').value = ''; refresh(); } });
        $('workflows').addEventListener('click', async (event) => { const button = event.target.closest('button[data-workflow]'); if (!button) return; const text = window.prompt(`Input for ${button.dataset.workflow}:`, 'Inspect the current foundation'); if (!text) return; $('workflow-output').textContent = 'Running...'; const response = await fetch(`/aether/workflows/${button.dataset.workflow}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text}) }); const data = await response.json(); $('workflow-output').textContent = response.ok ? (data.result || `Assigned to ${data.machine_id}`) : data.detail; });
        refresh(); setInterval(() => { countdown = Math.max(0, countdown - 1); $('refresh-count').textContent = countdown; if (countdown === 0) refresh(); }, 1000);
    </script>
</body>
</html>"""


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/skills")
def list_skills() -> dict:
    return {"skills": agent.describe_skills()}


@app.post("/skills/{skill}")
def use_skill(skill: str, request: SkillRequest) -> dict:
    try:
        return {"skill": skill, "result": agent.use_skill(skill, request.text)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/lattice")
def lattice_status() -> dict:
    return lattice.snapshot()


@app.post("/lattice/heartbeat")
def lattice_heartbeat(request: HeartbeatRequest) -> dict:
    try:
        state = lattice.heartbeat(**request.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"machine_id": request.machine_id, "state": state.value}


@app.post("/lattice/allocate")
def lattice_allocate(request: AllocationRequest) -> dict:
    try:
        if request.lease_seconds is None:
            machine_id = lattice.allocate(request.task, critical=request.critical)
            return {"task": request.task, "machine_id": machine_id, "leased": False}
        lease = lattice.acquire(
            request.task,
            duration=request.lease_seconds,
            critical=request.critical,
        )
        return {
            "task": lease.task,
            "machine_id": lease.machine_id,
            "leased": True,
            "expires_at": lease.expires_at,
        }
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
