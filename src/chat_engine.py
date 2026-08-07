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

def generate_final_answer(
    question: str,
    analysis_result: dict,
    api_key: str,
) -> str:
    """Generate the final response from analyzed evidence without performing retrieval."""

    documents = analysis_result.get("documents", [])

    verification = analysis_result.get("verification", {})

    missing_information = verification.get(
        "missing_information",
        [],
    )

    confidence = verification.get(
        "confidence",
        1.0,
    )

    if not documents:
        return "No relevant information was found in the uploaded documents."

    context = "\n\n".join(
        f"{doc['title']}\n{doc['evidence']}"
        for doc in documents
    )

    prompt = f"""
    You are an Executive Decision Assistant.

    Your goal is to help users make decisions quickly.

    Instructions:
    - Answer in 80–120 words.
    - Never exceed 150 words unless the user explicitly asks for a detailed analysis.
    - Give the recommendation first.
    - Mention only the top 3–4 decision factors.
    - Use Markdown headings.
    - Use bullet points.
    - Do not compare every company under separate headings.
    - Do not summarize every document.
    - Avoid repeating information.
    - Do not mention chunk numbers or retrieval details.

    Use this format:

    ## Recommendation
    <One concise recommendation>

    ## Reasons
    - Reason 1
    - Reason 2
    - Reason 3
    - Reason 4 (optional)

    ## Conclusion
    <One concluding sentence>

    Verification Summary

    Confidence Score:
    {confidence}

    Missing Information:
    {', '.join(missing_information) if missing_information else 'None'}

    If important information is missing, mention this briefly before giving the recommendation. Do not speculate or invent missing details.    

    Question:
    {question}

    Evidence:
    {context}
    """

    return call_gemini(prompt, api_key)

# =========================
# RAG Follow-up Answers
# =========================


def answer_follow_up(question: str, api_key: str, index: Any, chunks: list[ChunkRecord]) -> str:
    """Answer a user question with RAG context from the uploaded documents."""

    context_chunks = retrieve_context(index, chunks, question)

    if not context_chunks:
        return "Please upload and process documents before asking follow-up questions."

    analysis_result = {
        "documents": [
            {
                "title": chunk.document_title,
                "category": chunk.document_category,
                "chunk_index": chunk.chunk_index,
                "evidence": chunk.text,
            }
            for chunk in context_chunks
        ]
    }

    return generate_final_answer(
        question=question,
        analysis_result=analysis_result,
        api_key=api_key,
    )