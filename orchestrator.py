"""LangGraph orchestrator skeleton for the future Agentic AI architecture.

The current Streamlit app does not call this workflow yet. It exists as a
backward-compatible foundation for Milestone 3 agent orchestration.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.analyzer_agent import AnalyzerAgent
from agents.base_agent import AgentState
from agents.decision_agent import DecisionAgent
from agents.planner_agent import PlannerAgent
from agents.retrieval_agent import RetrievalAgent
from agents.verifier_agent import VerifierAgent


def build_agent_workflow():
    """Build and compile the skeleton LangGraph workflow."""

    planner = PlannerAgent()
    retriever = RetrievalAgent()
    analyzer = AnalyzerAgent()
    verifier = VerifierAgent()
    decision = DecisionAgent()

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner.execute)
    graph.add_node("retriever", retriever.execute)
    graph.add_node("analyzer", analyzer.execute)
    graph.add_node("verifier", verifier.execute)
    graph.add_node("decision", decision.execute)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "analyzer")
    graph.add_edge("analyzer", "verifier")
    graph.add_edge("verifier", "decision")
    graph.add_edge("decision", END)

    return graph.compile()


def run_agent_workflow(initial_state: AgentState) -> AgentState:
    """Run the skeleton workflow with the provided state."""

    workflow = build_agent_workflow()
    return workflow.invoke(initial_state)
