"""Decision agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent
from src.chat_engine import generate_final_answer

class DecisionAgent(BaseAgent):
    """Produces the future final decision response."""

    def __init__(self, api_key: str) -> None:
        """Initialize the decision agent."""

        super().__init__(name="decision")
        self.api_key = api_key

    def execute(self, state: AgentState) -> AgentState:
        """
        Generate the final response using the existing RAG chat engine.
        """

        answer = generate_final_answer(
            question=state["user_query"],
            analysis_result=state["analysis_result"],
            api_key=self.api_key,
        )

        state["final_response"] = answer
        state["current_agent"] = self.name
        state["workflow_status"] = "completed"

        return state
