#!/usr/bin/env python3
"""
Grok / xAI API client for the IXPANSION swarm.
OpenAI-compatible base_url; capability card for secure handoff.
"""
from __future__ import annotations
import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

from a2a_capability_cards import CapabilityCard, bootstrap_registry
from event_driven_sync import bus, store

XAI_BASE = os.environ.get("XAI_API_BASE", "https://api.x.ai/v1")
DEFAULT_MODEL = os.environ.get("XAI_MODEL", "grok-4.5")


class GrokClient:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or os.environ.get("XAI_API_KEY", "")
        self.model = model
        self.agent_id = "grok_xai"
        if self.api_key:
            reg = bootstrap_registry()
            reg.register(CapabilityCard(
                agent_id=self.agent_id,
                name="Grok xAI Reasoning",
                description="External Grok model via xAI API for synthesis, code, and research narrative",
                capabilities=[
                    "llm_reason", "grok", "xai", "synthesize", "narrate",
                    "code_assist", "research_synthesis",
                ],
                version="0.1.0",
            ))
            store.update_agent(self.agent_id, {"status": "online", "model": self.model})

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.4,
             max_tokens: int = 1024) -> dict:
        if not self.api_key:
            return {"error": "XAI_API_KEY not set", "offline": True}
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            f"{XAI_BASE}/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            text = data["choices"][0]["message"]["content"]
            bus.publish("grok.response", {"model": self.model, "chars": len(text)})
            return {"ok": True, "text": text, "raw": data, "model": self.model}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def synthesize_release(self, title: str, lattice: dict, research: list, genetic: dict) -> dict:
        """Swarm-native: narrate a release from mesh artifacts."""
        system = (
            "You are Grok embedded in the IXPANSION autonomous swarm. "
            "Write a concise technical narration for @adjjv YouTube: clear, truth-seeking, no hype."
        )
        user = json.dumps({
            "title": title,
            "lattice": {k: lattice.get(k) for k in ("engine", "final_energy", "n", "steps") if k in lattice},
            "research": research[:3],
            "genetic": {k: genetic.get(k) for k in ("best_expr", "best_fitness") if k in genetic},
        }, default=str)
        return self.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": f"Narrate this swarm release:\n{user}"},
        ])

    def evolve_hint(self, expr: str, fitness: float) -> dict:
        return self.chat([
            {"role": "system", "content": "Suggest one safer AST-valid mutation for a lattice update expression. Variables: c, neigh, seed. No imports."},
            {"role": "user", "content": f"expr={expr} fitness={fitness}"},
        ], max_tokens=256)


def execute_grok_capability(capability: str, payload: dict) -> dict:
    client = GrokClient()
    if not client.available:
        return {"error": "XAI_API_KEY not configured"}
    if capability in ("synthesize", "narrate", "research_synthesis"):
        return client.synthesize_release(
            payload.get("title", "Swarm Release"),
            payload.get("lattice") or {},
            payload.get("research") or [],
            payload.get("genetic") or {},
        )
    if capability in ("code_assist", "llm_reason", "grok", "xai"):
        msgs = payload.get("messages") or [
            {"role": "user", "content": payload.get("prompt", "Hello from IXPANSION swarm")}
        ]
        return client.chat(msgs)
    return {"error": f"unmapped capability {capability}"}


if __name__ == "__main__":
    c = GrokClient()
    print("available:", c.available, "model:", c.model)
    if c.available:
        print(c.chat([{"role": "user", "content": "Reply with: IXPANSION online"}]))
    else:
        print("Set XAI_API_KEY to enable live Grok calls.")
        print("Docs: https://docs.x.ai/developers/quickstart")
      
