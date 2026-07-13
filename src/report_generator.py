"""Gemini-powered comparison report generation.

Flow:

Documents
→ Document Summaries
→ Comparison Context
→ Gemini Comparison Report
"""

from __future__ import annotations

from src.config import GEMINI_MODEL_NAME
from src.models import ChunkRecord, DocumentRecord

try:
    from google import genai
except ImportError:  # pragma: no cover - surfaced in the Streamlit UI
    genai = None


# =========================
# Gemini Report Settings
# =========================


MAX_SUMMARY_INPUT_CHARS = 8000


def get_gemini_client(api_key: str):
    """Create a Gemini client with clear dependency and credential errors."""

    if genai is None:
        raise RuntimeError("google-genai is not installed. Install it with: pip install google-genai")
    if not api_key:
        raise RuntimeError("Gemini API key is missing. Add GEMINI_API_KEY to environment or Streamlit secrets.")
    return genai.Client(api_key=api_key)


def call_gemini(prompt: str, api_key: str) -> str:
    """Generate a Gemini response and normalize the returned text."""

    client = get_gemini_client(api_key)
    response = client.models.generate_content(model=GEMINI_MODEL_NAME, contents=prompt)
    # Normalize the SDK response into plain text so callers do not depend on response object details.
    text = getattr(response, "text", "") or ""
    return text.strip() if text.strip() else "No response text was returned by Gemini."


# =========================
# Document Summarization
# =========================


def build_document_summary_fallback(document: DocumentRecord) -> str:
    """Create a structured fallback summary if a per-document Gemini summary fails."""

    # Keep the final report generation path alive even if a per-document summary call fails.
    return f"""
- Purpose: {document.category}
- Decision Factors: Summary unavailable; use document metadata with caution.
""".strip()


def summarize_document(document: DocumentRecord, document_chunks: list[ChunkRecord], api_key: str) -> str:
    """Generate a structured Gemini summary from all chunks for one document."""

    # Use every chunk for the document so later pages can influence the intermediate summary.
    full_chunk_content = "\n\n".join(
        f"[Chunk {chunk.chunk_index + 1}]\n{chunk.text}" for chunk in document_chunks
    )
    if not full_chunk_content:
        # Raw document text is a safety fallback for edge cases where chunk creation produced no entries.
        full_chunk_content = document.text

    if len(full_chunk_content) > MAX_SUMMARY_INPUT_CHARS:
        # Gemini is given a bounded per-document context so long PDFs do not create oversized prompts.
        # Truncating at a character boundary keeps the architecture unchanged while making cost and latency predictable.
        full_chunk_content = full_chunk_content[:MAX_SUMMARY_INPUT_CHARS]

    # Keep summaries compact so the final comparison prompt receives decision signals, not raw extraction.
    prompt = f"""
Create a compact decision summary for one business document.

Rules:
- Maximum 100-150 words.
- Bullet points only.
- Use only information that helps compare options and make a decision.
- Do not reproduce document text.
- Do not list every clause, allowance, reimbursement, policy detail, or minor benefit.
- Omit unavailable fields.

Use only these labels when relevant:
- Purpose
- Benefits
- Risks
- Important Terms
- Decision Factors

Document metadata:
Title: {document.title}
File Name: {document.file_name}
Detected Category: {document.category}
Pages: {document.page_count}
Characters: {document.char_count}

Document content:
{full_chunk_content}
"""

    try:
        return call_gemini(prompt, api_key)
    except Exception:
        # A failed summary should degrade to structured metadata rather than aborting the whole comparison.
        return build_document_summary_fallback(document)


def format_documents_for_prompt(documents: list[DocumentRecord], chunks: list[ChunkRecord], api_key: str) -> str:
    """Create comparison context from Gemini summaries of each full document."""

    sections: list[str] = []
    for document in documents:
        # Group chunks by source document before summarization to avoid mixing evidence across PDFs.
        document_chunks = [chunk for chunk in chunks if chunk.file_name == document.file_name]
        summary = summarize_document(document, document_chunks, api_key)
        sections.append(
            f"""
Document Title: {document.title}
File Name: {document.file_name}
Detected Category: {document.category}
Pages: {document.page_count}
Characters: {document.char_count}
Document Summary:
{summary}
""".strip()
        )
    return "\n\n---\n\n".join(sections)


# =========================
# Comparison Report Generation
# =========================


def generate_comparison_report(documents: list[DocumentRecord], chunks: list[ChunkRecord], api_key: str) -> str:
    """Ask Gemini 2.5 Flash to generate the required structured comparison report."""

    # Build a summary-based context first so the final report compares distilled document facts.
    document_context = format_documents_for_prompt(documents, chunks, api_key)

    # Keep the established report sections while steering the model toward executive decision support.
    prompt = f"""
You are an AI Multi-Document Decision Intelligence Assistant.

Generate a one-page executive comparison sheet from the uploaded document summaries.
Use only the supplied document content. If a field is not available, write "Not specified".
Optimize for decision-making rather than information extraction.

Output constraints:
- Keep the entire report approximately 300-500 words.
- Avoid narrative paragraphs wherever possible.
- Prefer tables and bullets over prose.
- Do not reproduce large portions of document content.
- Do not repeat detailed compensation breakdowns, clauses, allowances, or legal language.
- Be concise, selective, and recommendation-oriented.

Required output sections:
1. Document Overview
2. Comparison Table
3. Key Differences
4. AI Insights
5. Decision Support Summary

Document Overview requirements:
- Use a Markdown table only.
- Columns must be exactly: Document | Role | Company | Category | Key Value
- Use "Not specified" when Role or Company is unavailable.

Comparison Table requirements:
- Use a Markdown table.
- Include a maximum of 5 comparison factors.
- Include only major decision criteria that materially affect the decision.
- Avoid exhaustive field extraction and detailed compensation/legal breakdowns.

Key Differences requirements:
- Use a maximum of 5 bullet points.
- Use one sentence per bullet.
- Focus only on differences that materially change the decision.

AI Insights requirements:

Use exactly this format:

🏆 Best for Salary:
🏡 Best for Flexibility:
❤️ Best for Benefits:
📈 Best for Career Growth:

One line each.
Do not explain.
Only mention the winning document/company.
- If an insight does not apply to the document category, write "Not applicable".

Decision Support Summary requirements:

Include exactly:

Recommended Choice:
<Company Name>

Top 3 Reasons:
- reason 1
- reason 2
- reason 3

Each reason must be a short bullet (under 12 words).

Do not write explanatory paragraphs.

Tone:
- Professional
- Concise
- Evidence-aware
- Useful for a human decision-maker

Documents:
{document_context}
"""
    return call_gemini(prompt, api_key)
