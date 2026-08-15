#!/usr/bin/env python3
"""
Swarm Orchestrator – One-Command Publish Package
Binds the full autonomous stack into a single coherent pipeline.

Usage:
  python swarm.py --publish-package
  python swarm.py --status
  python swarm.py --help
"""

import argparse
import subprocess
import signal
import os
import socket
import time
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Core layers
from event_driven_sync import bus, store, emit_heartbeat
from blackboard import Blackboard
from a2a_capability_cards import bootstrap_registry
from codebase_indexer import CodebaseIndexer
from indexer_agent import IndexerAgent
from task_handoff import TaskHandoff
from research_ingestion import ResearchIngester, seed_sample_research
from self_authoring import SelfAuthoringAgent
from content_pipeline import ContentPipelineAgent, OUTPUT_DIR
try:
    from ixpansion_executor import IXPansionExecutor
    HAS_IXPANSION = True
except Exception:
    HAS_IXPANSION = False
try:
    from shorts_pipeline import ShortsPipelineAgent
    HAS_SHORTS = True
except Exception:
    HAS_SHORTS = False


# Optional secure distributed handoff
try:
    from cross_node_handoff_secure import SecureCrossNodeHandoff
    HAS_SECURE = True
except Exception:
    HAS_SECURE = False


ROOT = Path("/home/workdir/artifacts")
RELEASE_DIR = ROOT / "releases"
RELEASE_DIR.mkdir(exist_ok=True)


def print_banner():
    print("=" * 60)
    print("  SWARM ORCHESTRATOR – Autonomous Agent Collective")
    print("=" * 60)



def _distributed_enrich(hub_url: str, timeout: float = 25.0):
    """
    One-shot secure handoff enrichment for publish-package.
    Connects briefly, requests research + code search, returns results.
    Requires an already-running secure hub + at least one worker.
    """
    if not HAS_SECURE:
        print("         secure handoff module not available")
        return None, None
    import asyncio

    async def _run():
        node = SecureCrossNodeHandoff(hub_url=hub_url, node_id="publish-orchestrator")
        # Monkey-patch run to do requests then exit
        results = {"code": None, "research": None}

        async def once():
            import websockets
            from websockets.client import connect
            async with connect(hub_url) as ws:
                node.ws = ws
                await node.announce()
                await asyncio.sleep(1.0)
                results["code"] = await node.request_remote_task(
                    required_capability="search",
                    task_type="code_search",
                    description="Publish-package code highlights",
                    payload={"query": "agent OR handoff OR indexer", "limit": 5},
                    timeout=timeout,
                )
                results["research"] = await node.request_remote_task(
                    required_capability="research_search",
                    task_type="research_query",
                    description="Publish-package research context",
                    payload={"query": "multi-agent OR capability", "limit": 4},
                    timeout=timeout,
                )
        try:
            await asyncio.wait_for(once(), timeout=timeout + 5)
        except Exception as e:
            print(f"         distributed enrich error: {e}")
        return results["code"], results["research"]

    try:
        return asyncio.run(_run())
    except Exception as e:
        print(f"         distributed enrich failed: {e}")
        return None, None



def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _find_port(start: int = 8765) -> int:
    for p in range(start, start + 40):
        if _port_free(p):
            return p
    raise RuntimeError("No free port for mesh hub")


class _MeshHandle:
    """Tracks auto-started hub + worker processes for graceful teardown."""
    def __init__(self):
        self.procs = []
        self.hub_url = None

    def stop(self):
        for proc in reversed(self.procs):
            if proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGINT)
                except Exception:
                    pass
        deadline = time.time() + 4
        for proc in self.procs:
            try:
                proc.wait(timeout=max(0.1, deadline - time.time()))
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self.procs.clear()
        print("         mesh stopped")


def _auto_start_mesh(workers: int = 1, token: str = "", base_port: int = 8765) -> _MeshHandle:
    """
    Start AuthHub + N secure workers in the background.
    Returns a handle for teardown.
    """
    handle = _MeshHandle()
    port = base_port if _port_free(base_port) else _find_port(base_port)
    handle.hub_url = f"ws://127.0.0.1:{port}"
    root = Path(__file__).resolve().parent
    py = sys.executable
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    if token:
        env["SWARM_TOKEN"] = token

    print(f"         starting AuthHub on {handle.hub_url}")
    hub_args = [py, str(root / "node_auth.py"), "--hub", "--port", str(port)]
    if token:
        hub_args += ["--token", token]
    hub = subprocess.Popen(hub_args, cwd=str(root), env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    handle.procs.append(hub)
    time.sleep(1.2)

    for i in range(workers):
        wargs = [
            py, str(root / "cross_node_handoff_secure.py"),
            "--join", handle.hub_url,
            "--node-id", f"auto-worker-{i+1}",
        ]
        if token:
            wargs += ["--token", token]
        w = subprocess.Popen(wargs, cwd=str(root), env=env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        handle.procs.append(w)
        time.sleep(0.4)
        print(f"         worker auto-worker-{i+1} up (pid={w.pid})")

    print(f"         mesh ready ({1 + workers} processes)")
    return handle


def cmd_status():
    """Show live status of all major components."""
    print_banner()
    print("\n[Status]")
    bb = Blackboard()
    snap = bb.snapshot()
    print(f"  Blackboard knowledge keys : {list(snap.get('knowledge', {}).keys())}")
    print(f"  Open tasks                : {len([t for t in snap.get('tasks', []) if t.get('status') == 'open'])}")

    indexer = CodebaseIndexer()
    if indexer.load():
        stats = indexer.get_stats()
        print(f"  Indexer chunks            : {stats.get('total_chunks', 0)}")
        print(f"  Indexer files             : {stats.get('files_indexed', 0)}")
    else:
        print("  Indexer                   : no index yet")

    reg = bootstrap_registry()
    print(f"  Registered agents         : {len(reg.list_all())}")
    for card in reg.list_all():
        print(f"    • {card['name']} ({', '.join(card['capabilities'][:3])}...)")

    state = store.get_state()
    print(f"  StateStore agents         : {list(state.get('agents', {}).keys())}")
    print(f"  Last sync                 : {state.get('last_sync')}")
    print()


def cmd_publish_package(title: str = None, distributed: bool = False, hub_url: str = "ws://127.0.0.1:8765"):
    """
    Full publish pipeline:
    1. Heartbeat + state sync
    2. Ensure index is fresh
    3. Ensure research is seeded
    4. Generate YouTube content package (pulls live code highlights)
    5. Assemble release bundle
    6. Write final manifest
    """
    print_banner()
    print("\n[Publish Package] Starting full pipeline...\n")
    mesh = None
    lattice_result = None
    shorts_meta = None
    final_title = title or "I Built an AI Swarm That Indexes Code, Ingests Research & Writes Its Own Tools"

    # 1. Heartbeat
    print("→ 1/6  Emitting heartbeat & state sync")
    emit_heartbeat("orchestrator")
    bus.publish("swarm.publish_start", {"ts": datetime.now(timezone.utc).isoformat()})

    # 2. Indexer
    print("→ 2/6  Refreshing codebase index")
    indexer_agent = IndexerAgent()
    stats = indexer_agent.get_stats()
    print(f"         Chunks available: {stats['stats'].get('total_chunks', 0)}")

    # 3. Research
    print("→ 3/6  Ensuring research knowledge is present")
    researcher = ResearchIngester()
    if len(researcher.docs) == 0:
        seed_sample_research(researcher)
    print(f"         Research docs: {len(researcher.docs)}")

    remote_code, remote_research = None, None
    mesh = None
    lattice_result = None
    shorts_meta = None
    final_title = title or "I Built an AI Swarm That Indexes Code, Ingests Research & Writes Its Own Tools"
    if distributed:
        print("→ 3b/6 Distributed secure enrichment")
        token = os.environ.get("SWARM_TOKEN", "")
        # Auto-start mesh if caller did not supply an external hub that is already up
        auto = True
        try:
            # quick probe: if something already listens, skip auto-start
            import socket as _s
            _host, _port_s = hub_url.replace("ws://", "").split(":")
            _port = int(_port_s)
            with _s.create_connection((_host, _port), timeout=0.4):
                auto = False
                print("         existing hub detected – using it")
        except Exception:
            auto = True

        if auto:
            print("         auto-starting secure mesh…")
            try:
                mesh = _auto_start_mesh(workers=1, token=token)
                hub_url = mesh.hub_url
            except Exception as e:
                print(f"         auto-start failed: {e}")
                mesh = None
        remote_code, remote_research = _distributed_enrich(hub_url)
        if remote_code:
            print(f"         remote code hits: {remote_code.get('count')}")
        if remote_research:
            print(f"         remote research hits: {remote_research.get('count')}")
        if not remote_code and not remote_research:
            print("         (no remote workers responded – using local only)")


    # 4. Content package
    print("→ 4/6  IXPANSION lattice snapshot (local)")
    lattice_result = None
    if HAS_IXPANSION:
        try:
            lattice_result = IXPansionExecutor().run("lattice", {"n": 16, "steps": 25, "seed": 0.42})
            print(f"         lattice energy={lattice_result.get('final_energy')} engine={lattice_result.get('engine')}")
        except Exception as e:
            print(f"         lattice skip: {e}")
    else:
        print("         IXPANSION not available")

    print("→ 4b/6 Generating YouTube content package")

    pipeline = ContentPipelineAgent()
    final_title = title or "I Built an AI Swarm That Indexes Code, Ingests Research & Writes Its Own Tools"
    pkg = pipeline.package_from_swarm_state(title=final_title)
    print(f"         Package ID: {pkg.id}")

    print("→ 4c/6 Short-form script")
    shorts_meta = None
    if HAS_SHORTS:
        try:
            shorts_meta = ShortsPipelineAgent().generate_from_swarm(topic=final_title).to_dict()
            print(f"         shorts id={shorts_meta.get('id')}")
        except Exception as e:
            print(f"         shorts skip: {e}")


    # 5. Assemble release bundle
    print("→ 5/6  Assembling release bundle")
    release_id = pkg.id
    release_path = RELEASE_DIR / release_id
    release_path.mkdir(exist_ok=True)

    # Copy content outputs
    for f in OUTPUT_DIR.glob(f"{pkg.id}*"):
        target = release_path / f.name
        target.write_text(f.read_text())
        print(f"         + {f.name}")

    # include latest shorts if generated
    shorts_dir = OUTPUT_DIR / "shorts"
    if shorts_meta and shorts_dir.exists():
        sid = shorts_meta.get("id")
        for f in shorts_dir.glob(f"{sid}*"):
            target = release_path / f.name
            target.write_text(f.read_text())
            print(f"         + {f.name}")

    # Include thumbnail links if present
    thumb_md = OUTPUT_DIR / "thumbnails.md"
    if thumb_md.exists():
        (release_path / "thumbnails.md").write_text(thumb_md.read_text())
        print("         + thumbnails.md")

    # 6. Manifest
    print("→ 6/6  Writing release manifest")
    manifest = {
        "release_id": release_id,
        "title": final_title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package": pkg.to_dict(),
        "indexer_stats": stats["stats"],
        "research_docs": len(researcher.docs),
        "distributed": bool(distributed),
        "lattice": lattice_result,
        "shorts": shorts_meta,
        "components": [
            "event_bus", "blackboard", "capability_cards",
            "codebase_indexer", "task_handoff", "research_ingestion",
            "self_authoring", "content_pipeline", "canva_thumbnails"
        ],
        "output_dir": str(release_path),
        "ready_for": "@adjjv YouTube"
    }
    manifest_path = release_path / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

    # Final blackboard post
    bb = Blackboard()
    bb.post("results", f"release:{release_id}", {
        "title": final_title,
        "path": str(release_path)
    }, agent_id="orchestrator")

    bus.publish("swarm.publish_complete", {"release_id": release_id})

    # 7. OpenClaw notify (live gateway or offline stub)
    print("→ 7/7  OpenClaw publish notify")
    openclaw_meta = None
    try:
        from openclaw_bridge import OpenClawBridge
        oc_manifest = {
            "channel": "@adjjv",
            "version": release_id,
            "title": final_title,
            "artifacts": [p.name for p in release_path.iterdir() if p.is_file()],
            "status": "ready",
            "output_dir": str(release_path),
        }
        oc = OpenClawBridge().publish_package_notify(oc_manifest)
        openclaw_meta = {"mode": oc.mode, "ok": oc.ok, "error": oc.error}
        manifest["openclaw"] = openclaw_meta
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
        print(f"         openclaw mode={oc.mode} ok={oc.ok}")
    except Exception as e:
        print(f"         openclaw skip: {e}")

    print("\n" + "=" * 60)
    print("  PUBLISH PACKAGE COMPLETE")
    print("=" * 60)
    print(f"  Release ID   : {release_id}")
    print(f"  Title        : {final_title}")
    print(f"  Output       : {release_path}")
    print(f"  Manifest     : {manifest_path}")
    print(f"  OpenClaw     : {openclaw_meta}")
    print(f"  Ready for    : @adjjv")
    print("=" * 60)
    return release_path


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Orchestrator – Autonomous Agent Collective"
    )
    parser.add_argument("--publish-package", action="store_true",
                        help="Run the full publish pipeline and assemble a release bundle")
    parser.add_argument("--title", type=str, default=None,
                        help="Custom title for the YouTube package")
    parser.add_argument("--status", action="store_true",
                        help="Show live status of all swarm components")
    parser.add_argument("--distributed", action="store_true",
                        help="Use secure cross-node handoff when mesh is available")
    parser.add_argument("--full-release", action="store_true",
                        help="Alias: publish-package + distributed + lattice + shorts")
    parser.add_argument("--hub", type=str, default="ws://127.0.0.1:8765",
                        help="Secure federation hub URL")
    args = parser.parse_args()

    if args.status:
        cmd_status()
    elif args.publish_package or getattr(args, 'full_release', False):
        dist = args.distributed or getattr(args, 'full_release', False)
        cmd_publish_package(title=args.title, distributed=dist, hub_url=args.hub)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python swarm.py --status")
        print("  python swarm.py --publish-package")
        print("  python swarm.py --publish-package --distributed")
        print('  python swarm.py --publish-package --title "My Custom Title"')


if __name__ == "__main__":
    main()
      
