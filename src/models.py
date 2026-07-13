"""Shared data models used across document processing, search, and UI layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocumentRecord:
    """Structured metadata and extracted content for one uploaded PDF."""

    file_name: str
    file_hash: str
    title: str
    category: str
    text: str
    page_count: int
    char_count: int


@dataclass
class ChunkRecord:
    """One searchable text chunk and the document metadata attached to it."""

    document_title: str
    document_category: str
    file_name: str
    chunk_index: int
    text: str


@dataclass
class ProcessingResult:
    """Result returned after extracting and classifying uploaded PDFs."""

    documents: list[DocumentRecord]
    warnings: list[str]
