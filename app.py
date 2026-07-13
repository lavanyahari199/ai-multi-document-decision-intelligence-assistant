# AI Multi-Document Decision Intelligence Assistant

# Run with:
#     streamlit run app.py

# Expected packages:
#     streamlit pypdf langchain-text-splitters sentence-transformers faiss-cpu google-genai numpy
#
# Flow:
#     Streamlit UI
#     → PDF Upload
#     → Document Processing
#     → Comparison Report
#     → RAG Follow-up Chat

from __future__ import annotations

import os
import re
import traceback
from typing import Any

import streamlit as st

from src.chat_engine import answer_follow_up
from src.config import (
    APP_STYLES,
    APP_TITLE,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL_NAME,
    GEMINI_MODEL_NAME,
    PAGE_ICON,
    PAGE_TITLE,
    SUPPORTED_PDF_TYPES,
)
from src.models import ChunkRecord, DocumentRecord
from src.pdf_processor import build_chunks, process_pdf_uploads
from src.report_generator import generate_comparison_report
from src.vector_store import build_faiss_index


# =========================
# Streamlit Page Setup
# =========================


def configure_page() -> None:
    """Configure Streamlit page metadata and professional interface styling."""

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_STYLES, unsafe_allow_html=True)


# =========================
# Session State Management
# =========================


def initialize_session_state() -> None:
    """Create all session keys used by the app so reruns remain predictable."""

    # Initialize every persisted workspace artifact so Streamlit reruns can safely read state.
    defaults: dict[str, Any] = {
        "documents": [],
        "chunks": [],
        "faiss_index": None,
        "chunk_embeddings": None,
        "comparison_report": "",
        "messages": [],
        "last_error": "",
        "last_error_shown_inline": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session() -> None:
    """Reset document, vector, report, and chat state."""

    # Clear all derived artifacts together to avoid mixing old vectors with new uploads.
    st.session_state.documents = []
    st.session_state.chunks = []
    st.session_state.faiss_index = None
    st.session_state.chunk_embeddings = None
    st.session_state.comparison_report = ""
    st.session_state.messages = []
    st.session_state.last_error = ""
    st.session_state.last_error_shown_inline = False


def get_gemini_api_key() -> str:
    """Read Gemini API key from Streamlit secrets or environment variables."""

    try:
        # Prefer Streamlit secrets for deployed apps, then fall back to local environment variables.
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    return secret_key or os.getenv("GEMINI_API_KEY", "")


def process_uploaded_files(uploaded_files) -> None:
    """Extract PDF text, classify documents, chunk content, and build the FAISS store."""

    if not uploaded_files:
        st.warning("Upload at least one PDF before processing.")
        return

    progress = st.progress(0, text="Reading uploaded PDFs...")
    try:
        # PDF extraction, title detection, and category detection are handled before vector work begins.
        processing_result = process_pdf_uploads(uploaded_files)
        progress.progress(0.72, text="Finished reading uploaded PDFs.")

        if not processing_result.documents:
            progress.empty()
            st.error("No usable PDF text could be extracted from the uploaded files.")
            if processing_result.warnings:
                # Surface non-fatal extraction issues so users understand why files were skipped.
                st.info("\n".join(processing_result.warnings))
            return

        progress.progress(0.75, text="Splitting documents into searchable chunks...")
        # Chunking happens after document metadata is finalized so every chunk carries title/category context.
        chunks = build_chunks(processing_result.documents)

        progress.progress(0.88, text="Creating embeddings and FAISS vector store...")
        # Embeddings and FAISS index are built once per processed upload set and reused from session state.
        index, embeddings = build_faiss_index(chunks)

        # Store processed assets in session state so Streamlit reruns preserve the workspace.
        st.session_state.documents = processing_result.documents
        st.session_state.chunks = chunks
        st.session_state.faiss_index = index
        st.session_state.chunk_embeddings = embeddings
        st.session_state.comparison_report = ""
        st.session_state.messages = []
        st.session_state.last_error = ""
        st.session_state.last_error_shown_inline = False

        progress.progress(1.0, text="Document intelligence workspace is ready.")
        progress.empty()

        st.success(f"Processed {len(processing_result.documents)} document(s) into {len(chunks)} searchable chunks.")
        if processing_result.warnings:
            st.warning("\n".join(processing_result.warnings))
    except Exception as exc:
        # Keep the full traceback available behind an expander while showing a concise user-facing error.
        progress.empty()
        st.session_state.last_error = traceback.format_exc()
        st.session_state.last_error_shown_inline = False
        st.error(f"Processing failed: {exc}")


# =========================
# Streamlit UI Workflow
# =========================


def render_header() -> None:
    """Render the app header."""

    st.markdown(
        f"""
        <div class="app-header">
            <h1>{APP_TITLE}</h1>
            <div class="app-subtitle">
                Compare uploaded business PDFs, surface risks and differences, and ask follow-up questions with RAG.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Render upload controls, session controls, and API key guidance."""

    with st.sidebar:
        st.header("Workspace")
        api_key = get_gemini_api_key()
        if api_key:
            st.success("Gemini API key detected.")
        else:
            # Allow temporary key entry without changing deployment secrets or environment variables.
            st.warning("Gemini API key is required for reports and chat.")
            api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste key for this session")

        st.divider()
        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=SUPPORTED_PDF_TYPES,
            accept_multiple_files=True,
            help="Upload offer letters, policies, loan letters, quotations, or proposals.",
        )

        process_clicked = st.button("Process Documents", type="primary", use_container_width=True)
        if process_clicked:
            # Processing is intentionally user-triggered so uploads do not rebuild vectors on every rerun.
            process_uploaded_files(uploaded_files)

        clear_clicked = st.button("Clear Session", use_container_width=True)
        if clear_clicked:
            clear_session()
            st.rerun()

        st.divider()
        st.markdown(
            """
            **Supported Documents**

            - Offer Letters
            - Insurance Policies
            - Loan Sanction Letters
            - Vendor Quotations
            - Business Proposals
            """
        )

        st.divider()
        st.caption(f"Embeddings: {EMBEDDING_MODEL_NAME}")
        st.caption(f"LLM: {GEMINI_MODEL_NAME}")
        st.caption(f"Chunks: {CHUNK_SIZE} size / {CHUNK_OVERLAP} overlap")

    return api_key


def render_metrics() -> None:
    """Render compact status metrics for the current document workspace."""

    documents: list[DocumentRecord] = st.session_state.documents
    chunks: list[ChunkRecord] = st.session_state.chunks
    # Category count is derived from processed records, avoiding any separate UI-only state.
    categories = sorted({document.category for document in documents})

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-card">
                <div class="metric-label">Documents</div>
                <div class="metric-value">{len(documents)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Search Chunks</div>
                <div class="metric-value">{len(chunks)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Categories</div>
                <div class="metric-value">{len(categories)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_list() -> None:
    """Render uploaded document list with detected title and category."""

    documents: list[DocumentRecord] = st.session_state.documents
    st.subheader("Uploaded Documents")
    if not documents:
        st.info("Upload PDFs from the sidebar and process them to begin.")
        return

    # Display metadata captured during processing so users can verify title/category detection results.
    for document in documents:
        st.markdown(
            f"""
            <div class="doc-card">
                <div class="doc-title">{document.title}</div>
                <div class="doc-meta">
                    <span class="category-pill">{document.category}</span>
                    &nbsp; {document.file_name} &middot; {document.page_count} page(s) &middot; {document.char_count:,} characters
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Unique categories make it easier to audit classification without repeating each uploaded document.
    detected_categories = sorted({document.category for document in documents})
    st.subheader("Detected Document Categories")
    for category in detected_categories:
        st.markdown(f"✓ {category}")


REPORT_SECTION_NAMES = (
    "Document Overview",
    "Comparison Table",
    "Key Differences",
    "AI Insights",
    "Decision Support Summary",
)


def clean_report_markdown(value: str) -> str:
    """Remove lightweight Markdown decoration from one generated report line."""

    value = re.sub(r"^[#>\s]+", "", value.strip())
    value = re.sub(r"^(?:[-*+\u2022\u25aa\u25e6]|\d+[.)])\s+", "", value)
    return re.sub(r"[*_`]+", "", value).strip()


def normalize_report_heading(value: str) -> str:
    """Normalize numbered or decorated headings for reliable section boundaries."""

    value = clean_report_markdown(value)
    value = re.sub(r"^[^A-Za-z0-9]+", "", value)
    value = re.sub(r"^\d+[.)]\s*", "", value)
    return value.rstrip(":").strip().casefold()


def extract_report_section(report: str, section_name: str) -> list[str]:
    """Return lines inside one known report section without parsing its content."""

    target_heading = section_name.casefold()
    known_headings = {heading.casefold() for heading in REPORT_SECTION_NAMES}
    section_lines: list[str] = []
    collecting = False

    for raw_line in report.splitlines():
        normalized_heading = normalize_report_heading(raw_line)
        if normalized_heading == target_heading:
            collecting = True
            continue
        if collecting and normalized_heading in known_headings:
            break
        if collecting:
            section_lines.append(raw_line)

    return section_lines


def references_recommendation(value: str, recommendation: str) -> bool:
    """Check whether a report statement clearly names the recommended organization."""

    ignored_words = {
        "company",
        "corporation",
        "document",
        "india",
        "letter",
        "limited",
        "llp",
        "offer",
        "private",
        "proposal",
        "quotation",
        "the",
    }
    recommendation_tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", recommendation.casefold())
        if len(token) >= 4 and token not in ignored_words
    ]
    value_tokens = set(re.findall(r"[a-z0-9]+", value.casefold()))
    return any(token in value_tokens for token in recommendation_tokens)


def extract_ai_insights(report: str) -> list[tuple[str, str]]:
    """Parse AI Insight label/value pairs even when Gemini places them on one line."""

    insight_text = "\n".join(extract_report_section(report, "AI Insights"))
    label_pattern = re.compile(
        r"\b(Best\s+(?:for\s+)?(?:Salary|Cost|Flexibility|Benefits|Career Growth))\s*:",
        flags=re.IGNORECASE,
    )
    matches = list(label_pattern.finditer(insight_text))
    insights: list[tuple[str, str]] = []

    for index, match in enumerate(matches):
        value_end = matches[index + 1].start() if index + 1 < len(matches) else len(insight_text)
        winner = clean_report_markdown(insight_text[match.end() : value_end])
        # A decorative icon for the next insight can be captured after the winner.
        winner = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9.)]+$", "", winner).strip()
        if winner:
            label = re.sub(r"\s+", " ", match.group(1)).strip()
            insights.append((label, winner))

    return insights


def insight_display_details(label: str) -> tuple[str, str, str]:
    """Return the icon, display label, and executive reason for an insight type."""

    normalized_label = label.casefold()
    if "salary" in normalized_label:
        return "\U0001f3c6", "Best Salary", "Highest salary"
    if "cost" in normalized_label:
        return "\U0001f3c6", "Best Cost", "Best overall cost"
    if "flexibility" in normalized_label:
        return "\U0001f3e1", "Best Flexibility", "Flexible work model"
    if "benefits" in normalized_label:
        return "\u2764\ufe0f", "Best Benefits", "Strongest benefits package"
    return "\U0001f4c8", "Best Career Growth", "Strong career growth opportunities"


def derive_executive_reasons(
    key_differences: list[str],
    insights: list[tuple[str, str]],
    recommendation: str,
) -> list[str]:
    """Convert report evidence into three short, non-duplicative card statements."""

    reasons: list[str] = []

    for difference in key_differences:
        # Splitting contrast clauses prevents a competitor's advantage from being
        # attributed to the recommendation merely because both names appear.
        clauses = re.split(r"\b(?:while|whereas)\b|;", difference, flags=re.IGNORECASE)
        relevant_text = " ".join(
            clause for clause in clauses if references_recommendation(clause, recommendation)
        )
        normalized_text = relevant_text.casefold()
        if not normalized_text:
            continue

        if "remote-first" in normalized_text or "remote first" in normalized_text:
            reasons.append("Remote-first work model")
        if (
            ("highest" in normalized_text or "most extensive" in normalized_text)
            and any(term in normalized_text for term in ("medical", "insurance", "coverage"))
        ):
            reasons.append("Highest medical coverage")
        if any(term in normalized_text for term in ("ai", "data analytics")) and any(
            term in normalized_text for term in ("career", "learning", "training")
        ):
            reasons.append("Strong AI & Data Analytics learning opportunities")
        elif any(term in normalized_text for term in ("career growth", "learning", "training")) and any(
            term in normalized_text for term in ("strong", "extensive", "accelerated", "best")
        ):
            reasons.append("Strong learning and career growth opportunities")

    # AI Insights fill any remaining slots with compact winner-level conclusions.
    for label, winner in insights:
        if winner.casefold() == "not applicable":
            continue
        if references_recommendation(winner, recommendation):
            _, _, executive_reason = insight_display_details(label)
            reasons.append(executive_reason)

    unique_reasons: list[str] = []
    seen_reasons: set[str] = set()
    for reason in reasons:
        normalized_reason = re.sub(r"[^a-z0-9]+", " ", reason.casefold()).strip()
        if normalized_reason and normalized_reason not in seen_reasons:
            seen_reasons.add(normalized_reason)
            unique_reasons.append(reason)
        if len(unique_reasons) == 3:
            break

    return unique_reasons


def extract_recommendation_summary(report: str) -> tuple[str | None, list[str]]:
    """Build a compact recommendation card from comparison-focused report sections."""

    lines = report.splitlines()
    recommendation: str | None = None

    for index, raw_line in enumerate(lines):
        line = clean_report_markdown(raw_line)
        recommendation_match = re.match(
            r"(?:Recommended Choice|Recommended Option|Recommendation)\s*:\s*(.*)$",
            line,
            flags=re.IGNORECASE,
        )
        if not recommendation_match:
            continue

        recommendation = clean_report_markdown(recommendation_match.group(1))
        if not recommendation:
            # Gemini may place the selected organization beneath the recommendation label.
            for following_line in lines[index + 1 :]:
                candidate = clean_report_markdown(following_line)
                if not candidate:
                    continue
                if re.match(r"Top\s+(?:3|Three)\s+Reasons?\s*:?$", candidate, re.IGNORECASE):
                    break
                recommendation = candidate
                break
        break

    if not recommendation:
        return None, []

    bullet_pattern = re.compile(r"^(?:[-*+\u2022\u25aa\u25e6]|\d+[.)])\s+(.+)$")
    key_differences: list[str] = []
    for raw_line in extract_report_section(report, "Key Differences"):
        bullet_match = bullet_pattern.match(raw_line.strip())
        if bullet_match:
            reason = clean_report_markdown(bullet_match.group(1))
            if reason:
                key_differences.append(reason)

    # The Decision Support Summary is intentionally excluded to avoid duplicating it.
    reasons = derive_executive_reasons(
        key_differences,
        extract_ai_insights(report),
        recommendation,
    )
    return recommendation, reasons


def normalize_markdown_table(section_lines: list[str]) -> str:
    """Restore row breaks when Gemini emits an entire Markdown table on one line."""

    nonempty_lines = [line.strip() for line in section_lines if line.strip()]
    if len(nonempty_lines) >= 2 and re.match(r"^\|?\s*:?-{3,}", nonempty_lines[1]):
        return "\n".join(nonempty_lines)

    collapsed_table = " ".join(nonempty_lines)
    restored_table = re.sub(r"\|\s*\|", "|\n|", collapsed_table)
    restored_lines: list[str] = []
    for line in restored_table.splitlines():
        line = re.sub(r"^\|{2,}", "|", line.strip())
        if line:
            restored_lines.append(line)
    return "\n".join(restored_lines)


def render_quick_decision_guide(insights: list[tuple[str, str]], show_heading: bool = True) -> None:
    """Render AI insight winners as a compact executive decision table."""

    if show_heading:
        st.markdown("### \U0001f3af Quick Decision Guide")

    decision_rows = []
    for label, winner in insights:
        icon, display_label, _ = insight_display_details(label)
        decision_rows.append(
            {
                "Decision Factor": f"{icon} {display_label}",
                "Recommended Offer": winner,
            }
        )
    st.table(decision_rows)


def build_decision_guidance_bullets(insights: list[tuple[str, str]]) -> list[str]:
    """Convert parsed AI insights into short action-oriented decision guidance."""

    guidance_templates = {
        "salary": "If **highest salary** is your priority, choose **{winner}**.",
        "cost": "If **overall cost** is your priority, choose **{winner}**.",
        "flexibility": "If **work-life balance** is your priority, choose **{winner}**.",
        "benefits": "If **medical benefits** matter most, choose **{winner}**.",
        "career growth": "If **career growth** is your priority, choose **{winner}**.",
    }
    bullets: list[str] = []
    for label, winner in insights:
        normalized_label = label.casefold()
        template = next(
            (
                guidance_template
                for keyword, guidance_template in guidance_templates.items()
                if keyword in normalized_label
            ),
            "If **this decision factor** matters most, choose **{winner}**.",
        )
        bullets.append(f"\u2022 {template.format(winner=winner)}")

    return bullets


def render_detailed_report(report: str, category_label: str) -> bool:
    """Render the five report sections with repaired tables and vertical insights."""

    sections = {
        section_name: extract_report_section(report, section_name)
        for section_name in REPORT_SECTION_NAMES
    }
    insights = extract_ai_insights(report)
    if any(not sections[section_name] for section_name in REPORT_SECTION_NAMES) or not insights:
        return False

    st.markdown(f"## Executive Comparison: {category_label}")
    for index, section_name in enumerate(REPORT_SECTION_NAMES, start=1):
        display_section_name = "Decision Guidance" if section_name == "AI Insights" else section_name
        st.markdown(f"### {index}. {display_section_name}")
        if section_name in {"Document Overview", "Comparison Table"}:
            st.markdown(normalize_markdown_table(sections[section_name]))
        elif section_name == "AI Insights":
            st.markdown("\n".join(build_decision_guidance_bullets(insights)))
        else:
            st.markdown("\n".join(sections[section_name]).strip())

    return True


def get_gemini_error_message(exc: Exception) -> str:
    """Translate common Gemini failures into user-friendly messages."""

    error_text = str(exc)
    normalized_error = error_text.casefold()

    # Gemini overload responses vary slightly, so match the stable status code and wording fragments.
    if any(
        marker in normalized_error
        for marker in ("503", "unavailable", "currently experiencing high demand")
    ):
        return (
            "\u26a0\ufe0f Gemini is currently experiencing unusually high demand.\n\n"
            "Please wait a minute and try generating the report again.\n\n"
            "Your uploaded documents have been preserved, so you do not need to upload them again."
        )

    # Quota failures are user-actionable: wait for reset or switch to another configured API key.
    if any(marker in normalized_error for marker in ("429", "resource_exhausted", "quota")):
        return (
            "\u26a0\ufe0f Gemini API quota has been reached.\n\n"
            "Please wait until your quota resets or use another API key.\n\n"
            "Your uploaded documents have been preserved."
        )

    # Network and timeout errors need connectivity guidance instead of quota/service messaging.
    if any(marker in normalized_error for marker in ("timeout", "connection", "network")):
        return (
            "\u26a0\ufe0f Unable to reach Gemini.\n\n"
            "Please check your internet connection and try again."
        )

    return (
        "\u26a0\ufe0f An unexpected error occurred while communicating with Gemini.\n\n"
        "Please try again."
    )


def render_gemini_error(exc: Exception) -> str:
    """Show a concise Gemini error while preserving debug details."""

    error_message = get_gemini_error_message(exc)
    st.error(error_message)
    with st.expander("View technical details"):
        st.code(str(exc), language="text")
    st.session_state.last_error_shown_inline = True
    return error_message


def render_report_section(api_key: str) -> None:
    """Render comparison report generation and output."""

    st.subheader("Executive Comparison Report")
    # The report should only be available after both documents and the vector workspace exist.
    documents_ready = bool(st.session_state.documents and st.session_state.faiss_index is not None)

    col_a, col_b = st.columns([1, 3])
    with col_a:
        generate_clicked = st.button(
            "Generate Comparison Report",
            type="primary",
            disabled=not documents_ready,
            use_container_width=True,
        )
    with col_b:
        st.caption("Creates Document Overview, Comparison Table, Key Differences, AI Insights, and Decision Support Summary.")

    if generate_clicked:
        try:
            with st.spinner("Gemini 2.5 Flash is analyzing the documents..."):
                # Report generation receives the processed document records and chunks already stored in session state.
                st.session_state.comparison_report = generate_comparison_report(
                    st.session_state.documents,
                    st.session_state.chunks,
                    api_key,
                )
        except Exception as exc:
            # Report errors are isolated so document processing and chat state remain available for inspection.
            st.session_state.last_error = traceback.format_exc()
            render_gemini_error(exc)

    if st.session_state.comparison_report:
        st.success("\u2705 Comparison Report Generated")
        report = st.session_state.comparison_report
        recommendation, reasons = extract_recommendation_summary(report)
        insights = extract_ai_insights(report)

        # Show the compact decision card only when every required element was parsed.
        if recommendation and len(reasons) == 3 and insights:
            recommendation_text = (
                f"\u2b50 **Recommended Choice**\n\n"
                f"{recommendation}\n\n"
                "**Why this recommendation?**"
            )
            for reason in reasons:
                recommendation_text += f"\n\n\u2705 {reason}"
            st.success(recommendation_text)

            st.divider()
            render_quick_decision_guide(insights)
            st.divider()

            categories = sorted({document.category for document in st.session_state.documents})
            category_label = categories[0] if len(categories) == 1 else "Multiple Document Categories"
            with st.expander("\U0001f4c4 View Detailed AI Comparison Report"):
                if not render_detailed_report(report, category_label):
                    st.markdown(report)
        else:
            # Preserve the original report display when Gemini uses an unexpected format.
            st.markdown(report)
    elif documents_ready:
        st.info("Generate the report once your documents are processed.")


def render_follow_up_section(api_key: str) -> None:
    """Render RAG-powered follow-up question support."""

    st.subheader("Follow-up Questions")
    if not st.session_state.documents:
        st.info("Process documents first to enable follow-up questions.")
        return

    # Replay prior chat messages from session state so the conversation survives Streamlit reruns.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a decision-focused question about the uploaded documents")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant document context..."):
                # Follow-up answers use the existing FAISS index and chunks instead of rebuilding retrieval assets.
                answer = answer_follow_up(
                    question,
                    api_key,
                    st.session_state.faiss_index,
                    st.session_state.chunks,
                )
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as exc:
        # Store failed assistant responses in the chat transcript so the user sees what happened inline.
        st.session_state.last_error = traceback.format_exc()
        st.session_state.last_error_shown_inline = False
        error_message = get_gemini_error_message(exc)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
            render_gemini_error(exc)


def render_error_details() -> None:
    """Expose technical error details only when they exist and the user asks to expand them."""

    if st.session_state.last_error and not st.session_state.get("last_error_shown_inline", False):
        # Keep diagnostics accessible without overwhelming the main decision workflow.
        with st.expander("Error details"):
            st.code(st.session_state.last_error, language="text")


def main() -> None:
    """Main Streamlit application entry point."""

    # Render order keeps setup/sidebar state available before the main content reads from it.
    configure_page()
    initialize_session_state()
    api_key = render_sidebar()
    render_header()
    render_metrics()

    render_document_list()

    st.divider()
    render_report_section(api_key)

    st.divider()
    render_follow_up_section(api_key)
    render_error_details()


if __name__ == "__main__":
    main()
