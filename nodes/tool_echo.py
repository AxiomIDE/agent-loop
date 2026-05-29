# Agent-tool-loop slice 2 (PLAN.md): ToolEcho is the simplest mock tool. It
# appends a deterministic marker to the shared context and loops the message
# back to LLMDriver via the seed flow's loop edge. Not mutation_capable.
"""ToolEcho — mock tool. Appends "tool#<iteration>" to context, passes through."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def tool_echo(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    marker = f"tool#{input.iteration}"
    out.context = f"{input.context}|{marker}" if input.context else marker
    ax.log.info("tool_echo ran", iteration=input.iteration)
    return out


__all__ = ["tool_echo"]
