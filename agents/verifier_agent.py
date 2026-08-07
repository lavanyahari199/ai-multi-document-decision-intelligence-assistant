"""Verifier agent skeleton for the future Agentic AI workflow."""

from __future__ import annotations

from agents.base_agent import AgentState, BaseAgent


class VerifierAgent(BaseAgent):
    """Validates future agent outputs against retrieved evidence."""

    def __init__(self) -> None:
        """Initialize the verifier agent."""

        super().__init__(name="verifier")

    def execute(self, state: AgentState) -> AgentState:
        """
        Verify that enough evidence exists before generating the final response.
        """

        analysis = state.get("analysis_result", {})
        documents = analysis.get("documents", [])

        required_information = state.get("required_information", [])

        covered_information = []

        combined_text = " ".join(
            document["evidence"].lower()
            for document in documents
        )

        keyword_map = {
            "salary": ["salary", "ctc", "package", "compensation"],
            "benefits": ["benefit", "insurance", "medical"],
            "leave": ["leave", "vacation", "pto"],
            "notice_period": ["notice"],
            "career_growth": ["career", "promotion", "learning", "training"],
        }

        for item in required_information:
            keywords = keyword_map.get(item, [])

            if any(keyword in combined_text for keyword in keywords):
                covered_information.append(item)

        verification = {
            "verified": True,
            "document_count": len(documents),
            "covered_information": covered_information,
            "missing_information": [],
            "issues": [],
        }

        if not documents:

            missing = [
                item
                for item in required_information
                if item not in covered_information
            ]

            verification["missing_information"] = missing

            if missing:
                verification["issues"].append(
                    f"Missing evidence for: {', '.join(missing)}"
                )

            verification["verified"] = False
            verification["issues"].append("No relevant document evidence found.")

        state["verification"] = verification

        if not documents:
            confidence = 0.0
        elif verification["missing_information"]:
            confidence = 0.7
        else:
            confidence = 1.0

        state["confidence"] = confidence
        
        state["errors"] = verification["issues"]
        state["current_agent"] = self.name
        state["workflow_status"] = "verification_completed"

        return state
