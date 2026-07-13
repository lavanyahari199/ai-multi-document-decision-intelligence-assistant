"""FAISS vector store creation and retrieval helpers.

Flow:

Chunks
→ Embeddings
→ FAISS Index
→ Similarity Search
→ Retrieved Context
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.config import TOP_K_CONTEXT
from src.embeddings import embed_query, embed_texts
from src.models import ChunkRecord

try:
    import faiss
except ImportError:  # pragma: no cover - surfaced in the Streamlit UI
    faiss = None


# =========================
# Vector Store Construction
# =========================


def build_faiss_index(chunks: list[ChunkRecord]) -> tuple[Any, np.ndarray]:
    """Embed chunks with all-MiniLM-L6-v2 and store them in a FAISS cosine-similarity index."""

    if faiss is None:
        raise RuntimeError("faiss-cpu is not installed. Install it with: pip install faiss-cpu")
    if not chunks:
        raise RuntimeError("No text chunks were created from the uploaded documents.")

    # Only raw chunk text is embedded; source metadata stays attached in the parallel ChunkRecord list.
    chunk_texts = [chunk.text for chunk in chunks]
    embeddings = embed_texts(chunk_texts)

    # Embeddings are normalized upstream, so inner product search behaves like cosine similarity.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    # FAISS stores vectors in the same order as chunks, making search indices map back to ChunkRecord items.
    index.add(embeddings)
    return index, embeddings


# =========================
# Similarity Search
# =========================


def retrieve_context(index: Any, chunks: list[ChunkRecord], question: str, top_k: int = TOP_K_CONTEXT) -> list[ChunkRecord]:
    """Retrieve the most relevant chunks for a follow-up question using FAISS."""

    if index is None or not chunks:
        # Retrieval can be called before processing; return no context instead of failing the chat flow.
        return []

    query_embedding = embed_query(question)
    # Avoid requesting more neighbors than the index contains for small document sets.
    search_k = min(top_k, len(chunks))
    _, indices = index.search(query_embedding, search_k)
    # Convert FAISS row ids back into chunk records while guarding against invalid ids.
    return [chunks[i] for i in indices[0] if 0 <= i < len(chunks)]
