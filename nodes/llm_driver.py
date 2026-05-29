# Agent-tool-loop (backlog/agent-tool-loop/PLAN.md): LLMDriver is the scripted,
# deterministic stand-in for the vision doc's LLM reasoner. NOT mutation_capable
# — it only decides. Determinism comes from encoding the plan in the goal string.
"""LLMDriver — scripted reasoner. Emits the per-turn dispatch + routing decision.

Goal-string script:
  - "turns=N"        → terminate (status="done") on turn N, else "continue".
  - "tools=A,B"      → tools dispatched EVERY turn (slices 2–5).
  - "tN=A,B" / "tN=" → PER-TURN override for turn N (slice 7); empty value means
                       dispatch nothing that turn (used on the terminate turn so
                       only the FlowComplete branch fires).

Precedence per turn: tN override > tools= > default ["ToolEcho"].
"""
from __future__ import annotations

import re

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext

DEFAULT_TURNS = 3
DEFAULT_TOOLS = ["ToolEcho"]


def _turn_budget(goal: str) -> int:
    m = re.search(r"turns=(\d+)", goal or "")
    if not m:
        return DEFAULT_TURNS
    try:
        return max(int(m.group(1)), 1)
    except ValueError:
        return DEFAULT_TURNS


def _tools_for_turn(goal: str, n: int) -> list[str]:
    g = goal or ""
    # Per-turn override "tN=..." (anchored on start or ';' so it can't match
    # inside "tools=" / "turns="). An explicit empty value → dispatch nothing.
    m = re.search(rf"(?:^|;)t{n}=([A-Za-z0-9_,]*)", g)
    if m is not None:
        return [t for t in m.group(1).split(",") if t]
    m2 = re.search(r"tools=([A-Za-z0-9_,]+)", g)
    if m2:
        names = [t for t in m2.group(1).split(",") if t]
        return names or list(DEFAULT_TOOLS)
    return list(DEFAULT_TOOLS)


def llm_driver(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    n = max(int(input.iteration), 0) + 1
    budget = _turn_budget(input.goal)
    tools = _tools_for_turn(input.goal, n)

    out = AgentMessage()
    out.goal = input.goal
    out.iteration = n
    out.tools.extend(tools)

    if n < budget:
        out.status = "continue"
        out.context = _append(input.context, f"reason#{n}")
        ax.log.info("driver: continue", iteration=n, budget=budget, tools=",".join(tools))
    else:
        out.status = "done"
        out.context = _append(input.context, f"reason#{n}=done")
        ax.log.info("driver: done", iteration=n, budget=budget, tools=",".join(tools))

    return out


def _append(context: str, marker: str) -> str:
    return f"{context}|{marker}" if context else marker


__all__ = ["llm_driver", "DEFAULT_TURNS", "DEFAULT_TOOLS"]
