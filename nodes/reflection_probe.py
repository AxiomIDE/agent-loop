# Agent-tool-loop slice 5 (PLAN.md) / GAP-4: ReflectionProbe reads
# ax.reflection.flow.edges and surfaces each conditional edge's condition
# SUMMARY (field/op/operands) into the shared context. This proves the platform
# now exposes the dispatch operand via reflection (previously only has_condition:
# bool) — the capability that lets an agent make idempotent AddTool decisions
# ("is ToolX already wired? then don't re-add it"). Not mutation_capable.
"""ReflectionProbe — emits the condition summaries it sees on the running flow."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext


def reflection_probe(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)
    seen = []
    try:
        for e in ax.reflection.flow.edges:
            if getattr(e, "has_condition", False) and getattr(e, "condition_summary", None) is not None:
                cs = e.condition_summary
                operands = ",".join(cs.operands)
                seen.append(f"{cs.field}:{cs.op}:{operands}")
    except Exception as exc:  # noqa: BLE001
        ax.log.error("reflection_probe failed", error=str(exc))
        seen = []
    marker = "cond=" + (";".join(sorted(seen)) if seen else "NONE")
    out.context = f"{input.context}|{marker}" if input.context else marker
    ax.log.info("reflection_probe", seen=";".join(sorted(seen)))
    return out


__all__ = ["reflection_probe"]
