# Agent-tool-loop slice 7 (PLAN.md) / GAP-1 + GAP-4: AddTool is the vision's
# mutation emitter. It dynamically splices a new tool (agent-loop-dyntool's
# DynTool) into the running flow, wired UNIFORMLY like the other tools —
# LLMDriver → DynTool (conditional dispatch edge, GAP-1) and DynTool →
# JoinPassthrough — by resolving the LLMDriver and JoinPassthrough instances via
# reflection. It is IDEMPOTENT (GAP-4): before splicing it inspects
# ax.reflection.flow.edges for an edge whose condition operand is already
# "DynTool" and skips re-adding if so, so it forks exactly once.
"""AddTool — idempotent mutation emitter; splices DynTool wired LLM->DynTool->Join."""
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


def _find_instance(ax: AxiomContext, node_name: str):
    try:
        for n in ax.reflection.flow.nodes:
            if n.name == node_name:
                return n.instance_id
    except Exception as exc:  # noqa: BLE001
        ax.log.error("add_tool reflection node lookup failed", node=node_name, error=str(exc))
    return None


def add_tool(ax: AxiomContext, input: AgentMessage) -> AgentMessage:
    out = AgentMessage()
    out.CopyFrom(input)

    if _already_wired(ax):
        out.context = _append(input.context, f"addtool#{input.iteration}=skip")
        ax.log.info("add_tool: DynTool already wired - skipping (idempotent)", iteration=input.iteration)
        return out

    llm_inst = _find_instance(ax, "LLMDriver")
    join_inst = _find_instance(ax, "JoinPassthrough")
    if llm_inst is None or join_inst is None:
        out.context = _append(input.context, f"addtool#{input.iteration}=no-anchor")
        ax.log.error("add_tool: could not resolve LLMDriver/JoinPassthrough via reflection",
                     llm=llm_inst, join=join_inst, iteration=input.iteration)
        return out

    try:
        # Place DynTool directly above AddTool. Reflection (ReflectionNode) does
        # not expose canvas x/y, so we can't read AddTool's runtime position to
        # compute "above myself" dynamically — we anchor to AddTool's fixed
        # fixture position (460, 400) and step up one canvas row (140). Without
        # this, mutationcompile auto-places the node at emitterX+480 (940, 400).
        new_iid = ax.mutation.flow.add_node(
            package=DYNTOOL_PACKAGE,
            version=DYNTOOL_VERSION,
            canvas_position=(460.0, 260.0),
        )
        # GAP-1: conditional dispatch edge LLMDriver -> DynTool (dormant unless the
        # reasoner puts "DynTool" in tools) - wired exactly like SearchTools/AddTool.
        ax.mutation.flow.add_edge(
            src_instance=llm_inst,
            dst_instance=new_iid,
            condition={"op": "EQ", "field": "tools", "value": DYNTOOL_OPERAND},
        )
        # DynTool -> JoinPassthrough, so the spliced tool fans into the same join.
        ax.mutation.flow.add_edge(src_instance=new_iid, dst_instance=join_inst)
        out.context = _append(input.context, f"addtool#{input.iteration}=spliced")
        ax.log.info("add_tool: spliced DynTool LLM->DynTool->Join", iteration=input.iteration,
                    new_iid=new_iid, llm=llm_inst, join=join_inst)
    except Exception as exc:  # noqa: BLE001
        ax.log.error("add_tool splice failed", error=str(exc))
    return out


def _append(context: str, marker: str) -> str:
    return f"{context}|{marker}" if context else marker


__all__ = ["add_tool"]
