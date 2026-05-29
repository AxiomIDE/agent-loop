# Agent-tool-loop slice 3 (PLAN.md): ToolA is a mock fan-out tool. Appends a
# distinct marker so the loop transcript shows it ran each turn. Not
# mutation_capable.
"""ToolA — mock tool. Appends "A#<iteration>" to context, passes through."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def tool_a(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    marker = f"A#{input.iteration}"
    out.context = f"{input.context}|{marker}" if input.context else marker
    ax.log.info("tool_a ran", iteration=input.iteration)
    return out


__all__ = ["tool_a"]
