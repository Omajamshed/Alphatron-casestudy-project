from langgraph.graph import StateGraph, START, END

from app.agents.state import ReviewState
from app.agents.checkpointer import checkpointer
from app.agents.nodes.extract_clauses import extract_clauses
from app.agents.nodes.classify_risk import classify_risk
from app.agents.nodes.retrieve_standard_terms import retrieve_standard_terms
from app.agents.nodes.draft_counter_clauses import draft_counter_clauses
from app.agents.nodes.validate import validate
from app.agents.nodes.human_review import human_review
from app.agents.nodes.export import export_node


def route_after_classify(state: ReviewState) -> str:
    route = state.get("route", "no_findings")
    if route == "has_findings":
        return "retrieve_standard_terms"
    return END


def route_after_validate(state: ReviewState) -> str:
    route = state.get("route", "proceed_to_review")
    if route == "retry":
        return "draft_counter_clauses"
    return "human_review"


def build_review_graph():
    builder = StateGraph(ReviewState)

    # Add nodes
    builder.add_node("extract_clauses", extract_clauses)
    builder.add_node("classify_risk", classify_risk)
    builder.add_node("retrieve_standard_terms", retrieve_standard_terms)
    builder.add_node("draft_counter_clauses", draft_counter_clauses)
    builder.add_node("validate", validate)
    builder.add_node("human_review", human_review)
    builder.add_node("export", export_node)

    # Add edges
    builder.add_edge(START, "extract_clauses")
    builder.add_edge("extract_clauses", "classify_risk")

    builder.add_conditional_edges(
        "classify_risk",
        route_after_classify,
        {
            "retrieve_standard_terms": "retrieve_standard_terms",
            END: END,
        },
    )

    builder.add_edge("retrieve_standard_terms", "draft_counter_clauses")
    builder.add_edge("draft_counter_clauses", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            "draft_counter_clauses": "draft_counter_clauses",
            "human_review": "human_review",
        },
    )

    builder.add_edge("human_review", "export")
    builder.add_edge("export", END)

    return builder.compile(checkpointer=checkpointer)


review_graph = build_review_graph()
