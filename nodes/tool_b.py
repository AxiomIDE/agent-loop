# Agent-tool-loop slice 3 (PLAN.md): ToolB is a second mock fan-out tool, the
# parallel sibling of ToolA. Its arrival is required by JoinPassthrough's
# JOIN_AND, so the flow only completes if ToolB also fired this turn.
"""ToolB — mock tool. Appends "B#<iteration>" to context, passes through."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def tool_b(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    marker = f"B#{input.iteration}"
    out.context = f"{input.context}|{marker}" if input.context else marker
    ax.log.info("tool_b ran", iteration=input.iteration)
    return out


__all__ = ["tool_b"]
