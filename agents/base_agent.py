"""Base abstractions for the future Agentic AI workflow.

This module is intentionally lightweight for Milestone 3 setup work. The
current production app continues to use the existing Streamlit and src/ flow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed between LangGraph agent nodes."""

    user_query: str

    intent: str
    execution_plan: list[str]
    required_information: list[str]

    retrieved_chunks: list[Any]

    analysis_result: dict[str, Any]

    verification: dict[str, Any]

    confidence: float

    errors: list[str]

    memory: dict[str, Any]

    current_agent: str
    workflow_status: str

    final_response: str


class BaseAgent(ABC):
    """Minimal base class that all agent skeletons inherit from."""

    def __init__(self, name: str) -> None:
        """Store the agent name for future tracing and observability."""

        self.name = name

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """Execute one agent step and return the updated graph state."""
