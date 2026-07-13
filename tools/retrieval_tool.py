"""Retrieval tool skeleton for future agent workflows."""

from __future__ import annotations

from typing import Any


class RetrievalTool:
    """Placeholder interface for future FAISS-backed retrieval orchestration."""

    def retrieve(self, query: str, context: dict[str, Any] | None = None) -> list[Any]:
        """Retrieve relevant context for a query."""

        # TODO: Reuse the existing vector_store retrieval logic in a future milestone.
        raise NotImplementedError("RetrievalTool.retrieve is not implemented yet.")
