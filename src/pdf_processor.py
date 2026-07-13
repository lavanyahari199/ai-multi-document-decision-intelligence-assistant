"""PDF extraction, title detection, category detection, and text chunking.

Flow:

PDF Upload
→ Text Extraction
→ Title Detection
→ Category Detection
→ Chunk Creation
"""

from __future__ import annotations

import hashlib
import io
import os
import re
from pathlib import Path

from pypdf import PdfReader

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, GEMINI_MODEL_NAME
from src.models import ChunkRecord, DocumentRecord, ProcessingResult

try:
    import streamlit as st
except ImportError:  # pragma: no cover - this module can still run outside Streamlit
    st = None

try:
    from google import genai
except ImportError:  # pragma: no cover - fallback logic keeps processing available
    genai = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover - surfaced in the Streamlit UI
    RecursiveCharacterTextSplitter = None


# =========================
# Document Category Rules
# =========================


VALID_DOCUMENT_CATEGORIES = {
    "Offer Letters",
    "Insurance Policies",
    "Loan Sanction Letters",
    "Vendor Quotations",
    "Business Proposals",
}

NORMALIZED_DOCUMENT_CATEGORIES = {
    category.lower(): category for category in VALID_DOCUMENT_CATEGORIES
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Offer Letters": [
        "offer letter",
        "employment offer",
        "joining date",
        "compensation",
        "salary",
        "designation",
        "probation",
        "employee benefits",
    ],
    "Insurance Policies": [
        "insurance policy",
        "policy number",
        "premium",
        "sum insured",
        "coverage",
        "claim",
        "exclusions",
        "deductible",
    ],
    "Loan Sanction Letters": [
        "loan sanction",
        "sanction letter",
        "loan amount",
        "interest rate",
        "emi",
        "repayment",
        "tenure",
        "collateral",
    ],
    "Vendor Quotations": [
        "quotation",
        "quote",
        "unit price",
        "total price",
        "validity",
        "vendor",
        "taxes",
        "delivery timeline",
    ],
    "Business Proposals": [
        "business proposal",
        "proposal",
        "scope of work",
        "project objective",
        "deliverables",
        "implementation plan",
        "commercial proposal",
        "executive summary",
    ],
}


def hash_file(file_bytes: bytes) -> str:
    """Create a stable hash so duplicate uploads can be detected."""

    return hashlib.sha256(file_bytes).hexdigest()


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving enough structure for title detection."""

    # Normalize extraction artifacts before downstream title/category logic sees the text.
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(uploaded_file) -> tuple[str, int]:
    """Extract text from an uploaded PDF using PyPDF."""

    # PyPDF works on a byte stream, so the uploaded Streamlit file is converted without writing to disk.
    file_bytes = uploaded_file.getvalue()
    reader = PdfReader(io.BytesIO(file_bytes))
    page_texts: list[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            # Page-level extraction lets one problematic page fail without discarding the whole document.
            page_text = page.extract_text() or ""
            page_texts.append(page_text)
        except Exception as exc:
            # Keep processing other pages and leave a visible marker for traceability.
            page_texts.append(f"\n[Text extraction failed on page {page_number}: {exc}]\n")

    return clean_text("\n\n".join(page_texts)), len(reader.pages)


def get_gemini_api_key() -> str:
    """Read Gemini API key from Streamlit secrets or environment variables."""

    secret_key = ""
    if st is not None:
        try:
            # Streamlit secrets support deployed apps; environment variables support local execution.
            secret_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            secret_key = ""
    return secret_key or os.getenv("GEMINI_API_KEY", "")


def call_gemini_safely(prompt: str) -> str:
    """Call Gemini when configured; return an empty string if unavailable or failing."""

    api_key = get_gemini_api_key()
    if genai is None or not api_key:
        # Missing Gemini support should not block PDF processing because deterministic fallbacks exist.
        return ""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=GEMINI_MODEL_NAME, contents=prompt)
        return (getattr(response, "text", "") or "").strip()
    except Exception:
        # Classification/title extraction falls back silently so upload processing remains resilient.
        return ""


def filename_title(file_name: str) -> str:
    """Create a readable title fallback from the uploaded filename."""

    return Path(file_name).stem.replace("_", " ").replace("-", " ").strip().title()


def extract_document_title_by_heuristic(text: str, file_name: str) -> str:
    """Infer a document title from early document content, falling back to filename."""

    fallback_title = filename_title(file_name)
    if not text:
        return fallback_title

    # The heuristic keeps the original behavior by selecting the first meaningful early line.
    early_lines = [line.strip(" :-\t") for line in text[:2500].splitlines()]
    generic_patterns = (
        r"^page\s+\d+",
        r"^date\s*[:\-]",
        r"^confidential$",
        r"^private\s+and\s+confidential$",
        r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$",
    )

    for line in early_lines:
        if not line or len(line) < 5 or len(line) > 140:
            continue
        # Skip headers and boilerplate that are common in PDFs but rarely represent the actual title.
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in generic_patterns):
            continue
        if sum(char.isalpha() for char in line) < 4:
            continue
        return re.sub(r"\s+", " ", line)

    return fallback_title


def extract_document_title_with_gemini(text: str, file_name: str) -> str:
    """Ask Gemini for a content-derived document title."""

    if not text:
        return ""

    # Limit title extraction context to the first few thousand characters where titles usually appear.
    prompt = f"""
Extract the best document title from the document content below.

Return only the document title. Do not include explanations, labels, quotes, or markdown.

Examples:
Employment Offer - Senior Business Analyst
SecureLife Health Protect Plus
Home Loan Sanction Letter

Filename:
{file_name}

Document content:
{text[:3000]}
"""
    title = call_gemini_safely(prompt)
    # Accept only a single concise line so unexpected Gemini formatting does not pollute metadata.
    title = title.splitlines()[0].strip(" \"'`:-") if title else ""
    if not title or len(title) < 5 or len(title) > 140:
        return ""
    if title.lower() in {"document title", "title", "not specified"}:
        return ""
    return re.sub(r"\s+", " ", title)


def is_strong_heuristic_title(title: str, file_name: str) -> bool:
    """Decide whether the heuristic title is good enough to avoid a Gemini call."""

    fallback_title = filename_title(file_name)
    if not title or title == fallback_title:
        return False
    if len(title) < 5 or len(title) > 140:
        return False
    return sum(char.isalpha() for char in title) >= 4


def extract_document_title(text: str, file_name: str) -> str:
    """Infer a document title using heuristic logic first, then Gemini, then filename."""

    # Prefer the cheap heuristic when it finds a usable content title, avoiding unnecessary Gemini calls.
    heuristic_title = extract_document_title_by_heuristic(text, file_name)
    if is_strong_heuristic_title(heuristic_title, file_name):
        return heuristic_title

    # Use Gemini only when the deterministic title looks weak or falls back to the filename.
    gemini_title = extract_document_title_with_gemini(text, file_name)
    if gemini_title:
        return gemini_title
    return filename_title(file_name)


def score_document_categories(text: str, file_name: str) -> dict[str, int]:
    """Score each allowed document category with the original keyword rules."""

    # Include the filename because uploaded business documents often encode their type in the name.
    searchable = f"{file_name}\n{text[:8000]}".lower()
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(3 if " " in keyword else 1 for keyword in keywords if keyword in searchable)
    return scores


def detect_document_category_by_keywords(text: str, file_name: str) -> str:
    """Classify with the original keyword-based fallback behavior."""

    scores = score_document_categories(text, file_name)
    best_category, best_score = max(scores.items(), key=lambda item: item[1])
    # Preserve the original default category when no keyword evidence is found.
    return best_category if best_score > 0 else "Business Proposals"


def should_use_gemini_category_classifier(scores: dict[str, int]) -> bool:
    """Decide whether keyword confidence is weak enough to need Gemini classification."""

    ranked_scores = sorted(scores.values(), reverse=True)
    best_score = ranked_scores[0] if ranked_scores else 0
    second_score = ranked_scores[1] if len(ranked_scores) > 1 else 0

    # Fall back to Gemini classification only when keyword confidence is weak or ambiguous.
    no_match = best_score <= 0
    weak_match = best_score < 5
    similar_scores = second_score > 0 and best_score - second_score <= 2
    return no_match or weak_match or similar_scores


def detect_document_category_with_gemini(text: str, file_name: str) -> str:
    """Ask Gemini to choose exactly one supported document category."""

    # The prompt constrains Gemini to the same closed category set used by the deterministic classifier.
    prompt = f"""
Classify this document into exactly one of the allowed categories.

Allowed categories:
- Offer Letters
- Insurance Policies
- Loan Sanction Letters
- Vendor Quotations
- Business Proposals

Return only one category name from the allowed list. Do not include explanations or markdown.

Filename:
{file_name}

Document content:
{text[:3000]}
"""
    category = call_gemini_safely(prompt)
    # Normalize valid category names while rejecting explanations or unsupported labels.
    category = category.splitlines()[0].strip(" \"'`:-.") if category else ""
    return NORMALIZED_DOCUMENT_CATEGORIES.get(category.lower(), "")


def detect_document_category(text: str, file_name: str) -> str:
    """Classify the document with keywords first, then Gemini when keyword confidence is low."""

    # Keyword classification remains the primary path for predictable, low-latency categorization.
    scores = score_document_categories(text, file_name)
    keyword_category = detect_document_category_by_keywords(text, file_name)
    if not should_use_gemini_category_classifier(scores):
        return keyword_category

    gemini_category = detect_document_category_with_gemini(text, file_name)
    # If Gemini fails or returns an invalid label, keep the deterministic keyword result.
    return gemini_category or keyword_category


# =========================
# Document Processing
# =========================


def process_pdf_uploads(uploaded_files) -> ProcessingResult:
    """Extract, title, and classify all uploaded PDFs without touching Streamlit state."""

    documents: list[DocumentRecord] = []
    seen_hashes: set[str] = set()
    warnings: list[str] = []

    for uploaded_file in uploaded_files:
        try:
            file_bytes = uploaded_file.getvalue()
            file_hash = hash_file(file_bytes)
            if file_hash in seen_hashes:
                # Duplicate detection prevents the same PDF from creating repeated chunks and vectors.
                warnings.append(f"Skipped duplicate upload: {uploaded_file.name}")
                continue

            seen_hashes.add(file_hash)
            # Extraction happens before metadata detection so title/category logic works from document content.
            text, page_count = extract_pdf_text(uploaded_file)
            if not text:
                # Scanned or image-only PDFs are skipped because there is no text to embed or compare.
                warnings.append(f"No extractable text found in: {uploaded_file.name}")
                continue

            # Metadata enrichment is kept alongside extraction so later chunks inherit clean document context.
            title = extract_document_title(text, uploaded_file.name)
            category = detect_document_category(text, uploaded_file.name)
            documents.append(
                DocumentRecord(
                    file_name=uploaded_file.name,
                    file_hash=file_hash,
                    title=title,
                    category=category,
                    text=text,
                    page_count=page_count,
                    char_count=len(text),
                )
            )
        except Exception as exc:
            # One failed upload should not prevent the remaining PDFs from being processed.
            warnings.append(f"Could not process {uploaded_file.name}: {exc}")

    return ProcessingResult(documents=documents, warnings=warnings)


def build_chunks(documents: list[DocumentRecord]) -> list[ChunkRecord]:
    """Split every document using RecursiveCharacterTextSplitter with requested settings."""

    if RecursiveCharacterTextSplitter is None:
        raise RuntimeError(
            "langchain-text-splitters is not installed. Install it with: pip install langchain-text-splitters"
        )

    # Recursive splitting preserves larger semantic boundaries before falling back to smaller separators.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[ChunkRecord] = []
    for document in documents:
        split_texts = splitter.split_text(document.text)
        for index, chunk_text in enumerate(split_texts):
            # Each chunk carries source metadata so retrieval and reports can cite document context later.
            chunks.append(
                ChunkRecord(
                    document_title=document.title,
                    document_category=document.category,
                    file_name=document.file_name,
                    chunk_index=index,
                    text=chunk_text,
                )
            )
    return chunks
