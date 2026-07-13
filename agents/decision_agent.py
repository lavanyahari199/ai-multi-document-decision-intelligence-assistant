"""Decision agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent


class DecisionAgent(BaseAgent):
    """Produces the future final decision response."""

    def __init__(self) -> None:
        """Initialize the decision agent."""

        super().__init__(name="decision")

    def execute(self, state: AgentState) -> AgentState:
        """Return state unchanged until decision synthesis is implemented."""

        # TODO: Convert verified analysis into the final user-facing response.
        return state
