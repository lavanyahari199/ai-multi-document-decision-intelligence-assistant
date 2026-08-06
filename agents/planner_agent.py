"""Planner agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent


class PlannerAgent(BaseAgent):
    """Plans the future multi-agent execution strategy."""

    def __init__(self) -> None:
        """Initialize the planner agent."""

        super().__init__(name="planner")

    def execute(self, state: AgentState) -> AgentState:
        """
        Analyze the user query and prepare an execution plan for the remaining agents.
        """

        query = state.get("user_query", "").lower()

        intent = "general_query"
        required_information: list[str] = []

        if any(word in query for word in ["salary", "ctc", "pay", "package"]):
            intent = "salary_comparison"
            required_information.append("salary")

        if any(word in query for word in ["benefit", "insurance", "medical"]):
            intent = "benefits_comparison"
            required_information.append("benefits")

        if any(word in query for word in ["leave", "vacation"]):
            required_information.append("leave")

        if any(word in query for word in ["notice"]):
            required_information.append("notice_period")

        if any(word in query for word in ["career", "growth", "promotion"]):
            required_information.append("career_growth")

        if any(word in query for word in ["recommend", "choose", "join", "best"]):
            intent = "recommendation"

        state["intent"] = intent
        state["required_information"] = required_information
        state["execution_plan"] = [
            "retrieve",
            "analyze",
            "verify",
            "decide",
        ]
        state["current_agent"] = self.name
        state["workflow_status"] = "planning_completed"

        return state
