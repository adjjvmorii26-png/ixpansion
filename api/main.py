from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import Agent
from lattice_stack import LatticePolicy, Machine, MachineLattice

app = FastAPI(title="IXPANSION API", version="1.2.0-rc3")
agent = Agent()
lattice = MachineLattice(
    [
        Machine("api-healthy-0", health=0.95, capacity=0.8),
        Machine("api-reuse-0", health=0.55, capacity=0.35),
    ],
    policy=LatticePolicy(heartbeat_timeout=300),
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


@app.get("/")
def read_root() -> dict:
    return {"service": "ixpansion", "status": "ok"}


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
