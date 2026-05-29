# Agent-tool-loop slice 7 (PLAN.md): SearchTools is the vision's marketplace
# search node — here a deterministic mock. It "finds" a tool and records that
# in the shared context, then feeds JoinPassthrough. Not mutation_capable.
"""SearchTools — mock marketplace search. Appends "search#<iteration>"."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def search_tools(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    out.context = f"{input.context}|search#{input.iteration}" if input.context else f"search#{input.iteration}"
    ax.log.info("search_tools ran", iteration=input.iteration)
    return out


__all__ = ["search_tools"]
