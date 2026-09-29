from langgraph.graph import END, START, StateGraph

from .nodes import (
    classify_node,
    final_node,
    fix_node,
    response_node,
    review_node,
    understand_node,
)
from .state import AgentState

MAX_FIX_CYCLES = 2


def review_router(state: AgentState) -> str:
    """Route to final when approved or after the maximum two fix cycles."""
    if state["approved"]:
        return "final"
    if state["iteration_count"] >= MAX_FIX_CYCLES:
        return "final"
    return "fix"


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("understand", understand_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("response", response_node)
    workflow.add_node("review", review_node)
    workflow.add_node("fix", fix_node)
    workflow.add_node("final", final_node)

    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "classify")
    workflow.add_edge("classify", "response")
    workflow.add_edge("response", "review")

    workflow.add_conditional_edges(
        "review",
        review_router,
        {
            "fix": "fix",
            "final": "final",
        },
    )

    workflow.add_edge("fix", "review")
    workflow.add_edge("final", END)

    return workflow.compile()


graph = build_graph()
