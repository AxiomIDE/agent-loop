# Agent-tool-loop slice 7 (PLAN.md) / GAP-1 + GAP-4: AddTool is the vision's
# mutation emitter. It dynamically splices a new tool (agent-loop-dyntool's
# DynTool) into the running flow behind a CONDITIONAL dispatch edge
# ("DynTool" in tools) — GAP-1. It is IDEMPOTENT (GAP-4): before splicing it
# inspects ax.reflection.flow.edges for an edge whose condition operand is
# already "DynTool", and skips re-adding if so. So it forks exactly once across
# the agent's turns, no matter how many times the reasoner routes to it.
"""AddTool — idempotent mutation emitter; splices DynTool behind a cond edge."""
from __future__ import annotations

from gen.messages_pb2 import AgentMessage
from gen.axiom_context import AxiomContext

DYNTOOL_PACKAGE = "axiom-official/agent-loop-dyntool"
DYNTOOL_VERSION = "0.1.0"
DYNTOOL_OPERAND = "DynTool"


def _already_wired(ax: AxiomContext) -> bool:
    # GAP-4: a dispatch edge already carries operand DYNTOOL_OPERAND.
    try:
        for e in ax.reflection.flow.edges:
            cs = getattr(e, "condition_summary", None)
            if cs is not None and DYNTOOL_OPERAND in list(cs.operands):
                return True
    except Exception as exc:  # noqa: BLE001
        ax.log.error("add_tool reflection check failed", error=str(exc))
    return False


def add_tool(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)

    if _already_wired(ax):
        out.context = _append(input.context, f"addtool#{input.iteration}=skip")
        ax.log.info("add_tool: DynTool already wired — skipping (idempotent)", iteration=input.iteration)
        return out

    try:
        new_iid = ax.mutation.flow.add_node(package=DYNTOOL_PACKAGE, version=DYNTOOL_VERSION)
        pos = ax.reflection.flow.position
        # GAP-1: conditional dispatch edge — DynTool only fires when the reasoner
        # puts "DynTool" in tools (dormant otherwise; the splice is the point).
        ax.mutation.flow.add_edge(
            src_instance=pos.current_instance,
            dst_instance=new_iid,
            condition={"op": "EQ", "field": "tools", "value": DYNTOOL_OPERAND},
        )
        out.context = _append(input.context, f"addtool#{input.iteration}=spliced")
        ax.log.info("add_tool: spliced DynTool", iteration=input.iteration, new_iid=new_iid)
    except Exception as exc:  # noqa: BLE001
        ax.log.error("add_tool splice failed", error=str(exc))
    return out


def _append(context: str, marker: str) -> str:
    return f"{context}|{marker}" if context else marker


__all__ = ["add_tool"]
