"""Retrieval agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent


class RetrievalAgent(BaseAgent):
    """Coordinates future retrieval operations through retrieval tools."""

    def __init__(self) -> None:
        """Initialize the retrieval agent."""

        super().__init__(name="retriever")

    def execute(self, state: AgentState) -> AgentState:
        """Return state unchanged until retrieval orchestration is implemented."""

        # TODO: Call retrieval tools and attach relevant chunks to AgentState.
        return state
