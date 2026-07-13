"""SentenceTransformer embedding utilities."""

from __future__ import annotations

import numpy as np
import streamlit as st

from src.config import EMBEDDING_MODEL_NAME

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - surfaced in the Streamlit UI
    SentenceTransformer = None


@st.cache_resource(show_spinner=False)
def load_embedding_model() -> SentenceTransformer:
    """Load and cache the SentenceTransformer model once per Streamlit session."""

    if SentenceTransformer is None:
        raise RuntimeError(
            "sentence-transformers is not installed. Install it with: pip install sentence-transformers"
        )
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """Create normalized float32 embeddings for document chunks."""

    model = load_embedding_model()
    return model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")


def embed_query(question: str) -> np.ndarray:
    """Create one normalized float32 query embedding for FAISS retrieval."""

    model = load_embedding_model()
    return model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")
