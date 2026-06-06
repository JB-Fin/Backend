from langgraph.graph import StateGraph, START, END

from app.agents.review_agent import run_review_agent
from app.agents.revision_agent import run_revision_agent
from app.agents.report_agent import run_report_agent
from app.graphs.state import ReviewState

def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("review_agent", run_review_agent)
    graph.add_node("revision_agent", run_revision_agent)
    graph.add_node("report_agent", run_report_agent)

    graph.add_edge(START, "review_agent")
    graph.add_edge("review_agent", "revision_agent")
    graph.add_edge("revision_agent", "report_agent")
    graph.add_edge("report_agent", END)

    return graph.compile()


review_graph = build_review_graph()