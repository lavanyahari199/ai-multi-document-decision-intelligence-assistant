"""Search tool skeleton for future agent workflows."""

from __future__ import annotations

from typing import Any
from src.vector_store import retrieve_context

class SearchTool:
    """Thin wrapper around the existing FAISS retrieval implementation."""

    def __init__(self, faiss_index, chunks) -> None:
        self.faiss_index = faiss_index
        self.chunks = chunks

    def search(self, query: str):
        """Return the most relevant chunks for a query."""

        return retrieve_context(
            index=self.faiss_index,
            chunks=self.chunks,
            question=query,
        )