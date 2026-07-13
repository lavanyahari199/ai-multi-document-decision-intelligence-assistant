"""RAG follow-up question answering.

Flow:

User Question
→ Similarity Search
→ Retrieved Context
→ Gemini Grounded Answer
"""

from __future__ import annotations

from typing import Any

from src.models import ChunkRecord
from src.report_generator import call_gemini
from src.vector_store import retrieve_context


# =========================
# RAG Follow-up Answers
# =========================


def answer_follow_up(question: str, api_key: str, index: Any, chunks: list[ChunkRecord]) -> str:
    """Answer a user question with RAG context from the uploaded documents."""

    # Retrieve only the most relevant chunks so the answer is grounded in uploaded documents.
    context_chunks = retrieve_context(index, chunks, question)
    if not context_chunks:
        # Chat can be opened before processing; provide a helpful response instead of raising.
        return "Please upload and process documents before asking follow-up questions."

    # Include source metadata beside each chunk so Gemini can cite document titles naturally.
    context = "\n\n".join(
        f"[{chunk.document_title} | {chunk.document_category} | chunk {chunk.chunk_index + 1}]\n{chunk.text}"
        for chunk in context_chunks
    )
    # The prompt keeps answers constrained to retrieved evidence while steering Gemini toward decision support.
    prompt = f"""
You are an Executive Decision Assistant answering a follow-up question using retrieval-augmented generation.

Rules:
- Answer only from the retrieved context.
- Cite document titles naturally in the answer.
- If the answer is not present in the context, say that the uploaded documents do not specify it.
- Start with a direct answer in 1-2 sentences.
- Prioritize the recommendation before supporting details.
- Compare only the documents relevant to the question.
- Mention only decision-making factors that affect the answer.
- Avoid repeating document wording or summarizing every retrieved chunk.
- Keep the answer concise, ideally 80-150 words.
- Exceed 150 words only if the user explicitly asks for detailed analysis.
- Do not mention chunk numbers or retrieval details.

Preferred structure:
Answer
(1-2 direct sentences)

Key Comparison
• Point 1
• Point 2

Recommendation
One short concluding sentence, only if a recommendation is appropriate.

Question:
{question}

Retrieved context:
{context}
"""
    return call_gemini(prompt, api_key)
