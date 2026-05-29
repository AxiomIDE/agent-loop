# Agent-tool-loop slice 3 (PLAN.md): JoinPassthrough is the fan-in merge node.
# It is a JOIN_AND consumer over the fired tool edges; a static ADR-045
# compose_plan assembles its AgentMessage input from one incident edge so the
# loop stays typed (AgentMessage in, AgentMessage out) — see the fixture. The
# node body just records that the merge fired this turn and passes through.
# Not mutation_capable in slice 3a (the per-turn join reconfig is GAP-2/slice 3b).
"""JoinPassthrough — fan-in merge. Appends "join#<iteration>", passes through."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def join_passthrough(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    marker = f"join#{input.iteration}"
    out.context = f"{input.context}|{marker}" if input.context else marker
    ax.log.info("join_passthrough merged", iteration=input.iteration, status=input.status)
    return out


__all__ = ["join_passthrough"]
