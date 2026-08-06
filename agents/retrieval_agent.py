"""Retrieval agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent
from tools.search_tool import SearchTool

class RetrievalAgent(BaseAgent):
    """Coordinates future retrieval operations through retrieval tools."""

    def __init__(self, faiss_index, chunks) -> None:
        """Initialize the retrieval agent."""

        super().__init__(name="retriever")

        self.search_tool = SearchTool(
            faiss_index=faiss_index,
            chunks=chunks
        )

    def execute(self, state: AgentState) -> AgentState:
        """Retrieve relevant document chunks."""

        retrieved_chunks = self.search_tool.search(
            query=state["user_query"]
        )

        state["retrieved_chunks"] = retrieved_chunks
        state["current_agent"] = self.name
        state["workflow_status"] = "retrieval_completed"

        return state
