"""Planner agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent


class PlannerAgent(BaseAgent):
    """Plans the future multi-agent execution strategy."""

    def __init__(self) -> None:
        """Initialize the planner agent."""

        super().__init__(name="planner")

    def execute(self, state: AgentState) -> AgentState:
        """Return state unchanged until planning logic is implemented."""

        # TODO: Infer user intent and create an execution plan.
        return state
