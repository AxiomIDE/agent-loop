# Agent-tool-loop slice 2 (PLAN.md): FlowComplete is the seed flow's terminal
# node. LLMDriver routes here on the status=="done" branch. It passes the
# accumulated AgentMessage through unchanged so the SPA's result panel renders
# the full loop transcript (the e2e asserts on context). Not mutation_capable.
"""FlowComplete — terminal passthrough. Emits the final AgentMessage."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def flow_complete(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    ax.log.info("flow_complete (terminal)", iteration=input.iteration, context=input.context[:120])
    return out


__all__ = ["flow_complete"]
