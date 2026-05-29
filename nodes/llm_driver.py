# Agent-tool-loop slice 2 (backlog/agent-tool-loop/PLAN.md): LLMDriver is the
# scripted, deterministic stand-in for the vision doc's LLM reasoner. It is NOT
# mutation_capable — it only decides; later slices add the mutation-emitting
# tools. Determinism comes from encoding the driver's plan in the goal string
# (e.g. "turns=3") and keying decisions off the turn counter, so the e2e needs
# no real model call and no secrets.
"""LLMDriver — scripted reasoner. Emits the per-turn routing decision.

Each turn it increments `iteration` and sets `status`:
  - iteration < turns  → status="continue", tools=["ToolEcho"]   (loop a tool)
  - iteration >= turns → status="done"                           (terminate)

The seed flow branches on `status` (EQ conditions), so with turns=3 the tool
runs on turns 1 and 2 and the flow terminates on turn 3.
"""
from __future__ import annotations

import re

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext

DEFAULT_TURNS = 3


def _turn_budget(goal: str) -> int:
    m = re.search(r"turns=(\d+)", goal or "")
    if not m:
        return DEFAULT_TURNS
    try:
        return max(int(m.group(1)), 1)
    except ValueError:
        return DEFAULT_TURNS


def llm_driver(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    n = max(int(input.iteration), 0) + 1
    budget = _turn_budget(input.goal)

    out = AgentMessage()
    out.goal = input.goal
    out.iteration = n

    if n < budget:
        out.status = "continue"
        out.tools.append("ToolEcho")
        out.context = _append(input.context, f"reason#{n}")
        ax.log.info("driver: continue", iteration=n, budget=budget)
    else:
        out.status = "done"
        out.context = _append(input.context, f"reason#{n}=done")
        ax.log.info("driver: done", iteration=n, budget=budget)

    return out


def _append(context: str, marker: str) -> str:
    return f"{context}|{marker}" if context else marker


__all__ = ["llm_driver", "DEFAULT_TURNS"]
