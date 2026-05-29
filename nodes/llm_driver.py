# Agent-tool-loop (backlog/agent-tool-loop/PLAN.md): LLMDriver is the scripted,
# deterministic stand-in for the vision doc's LLM reasoner. It is NOT
# mutation_capable — it only decides. Determinism comes from encoding the
# driver's plan in the goal string, so the e2e needs no model call and no
# secrets.
"""LLMDriver — scripted reasoner. Emits the per-turn dispatch + routing decision.

The goal string carries the script:
  - "turns=N"            → terminate (status="done") on turn N, else "continue".
  - "tools=A,B,..."      → the tool names to dispatch each turn (the vision's
                           `repeated tools` fan-out field). Defaults to
                           ["ToolEcho"] (slice-2 single-tool back-edge loop).

Each turn it increments `iteration`, sets `status`, and populates `tools`. The
seed flow dispatches on `tools` membership (EQ on the repeated field) and routes
on `status` (slice 2: directly off LLMDriver; slice 3+: after the join).
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


def _tools_for_run(goal: str) -> list[str]:
    m = re.search(r"tools=([A-Za-z0-9_,]+)", goal or "")
    if not m:
        return list(DEFAULT_TOOLS)
    names = [t for t in m.group(1).split(",") if t]
    return names or list(DEFAULT_TOOLS)


def llm_driver(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    n = max(int(input.iteration), 0) + 1
    budget = _turn_budget(input.goal)
    tools = _tools_for_run(input.goal)

    out = AgentMessage()
    out.goal = input.goal
    out.iteration = n
    # Dispatch the configured tools every turn. Whether the loop continues or
    # terminates is decided by `status` routing (slice 2: off LLMDriver; slice
    # 3+: after the join), NOT by clearing tools — so the join's incident edges
    # stay satisfied on the terminal turn too.
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
