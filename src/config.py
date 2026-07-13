"""Application configuration constants for the decision intelligence assistant."""

APP_TITLE = "AI Multi-Document Decision Intelligence Assistant"
PAGE_TITLE = "Decision Intelligence Assistant"
PAGE_ICON = "DI"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_CONTEXT = 8

SUPPORTED_PDF_TYPES = ["pdf"]

APP_STYLES = """
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }
    .app-header {
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
    }
    .app-subtitle {
        color: #4b5563;
        font-size: 1rem;
        margin-top: -0.25rem;
    }
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 1.25rem;
    }
    .metric-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        background: #ffffff;
    }
    .metric-label {
        color: #6b7280;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .metric-value {
        color: #111827;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 0.15rem;
    }
    .doc-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
        background: #ffffff;
    }
    .doc-title {
        color: #111827;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .doc-meta {
        color: #4b5563;
        font-size: 0.88rem;
    }
    .category-pill {
        display: inline-block;
        border: 1px solid #cbd5e1;
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        color: #1f2937;
        background: #f8fafc;
        font-size: 0.78rem;
        font-weight: 600;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }
</style>
"""
