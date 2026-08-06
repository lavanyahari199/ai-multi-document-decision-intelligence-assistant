# Milestone 1 – Project Setup and Documentation

## Objective

Initiate the AI Multi-Document Decision Intelligence Assistant project by defining the problem statement, project scope, supported document types, expected outputs, architecture, and development roadmap.

## Problem Statement

In many real-world scenarios, users need to compare multiple documents before making important personal or business decisions. Examples include job offers, insurance policies, loan documents, vendor quotations, and business proposals.

Manually reviewing and comparing these documents can be time-consuming, error-prone, and overwhelming. Users often struggle to identify key differences, understand trade-offs, and determine which option best aligns with their priorities.

## Proposed Solution

The AI Multi-Document Decision Intelligence Assistant aims to simplify document comparison by leveraging Generative AI to:

* Extract important information from uploaded documents
* Generate structured comparisons
* Highlight key differences
* Produce AI-generated insights
* Provide decision-support recommendations

The application is designed to support informed decision-making rather than make decisions on behalf of users.

## Project Scope

### Supported Document Types

The application will initially support:

1. Job Offers
2. Insurance Policies
3. Loan Documents
4. Vendor Quotations
5. Business Proposals

These document categories were selected because they represent common business and personal decision-making scenarios.

## Comparison Output Structure

Every comparison will generate the following sections:

### 1. Document Overview

Provides a high-level summary of each uploaded document.

### 2. Comparison Table

Generates a structured side-by-side comparison of important attributes.

### 3. Key Differences

Highlights the most significant differences identified across documents.

### 4. AI Insights

Provides business-oriented observations and analysis.

### 5. Decision Support Summary

Generates recommendation-oriented guidance based on user priorities and document characteristics.

## Initial Architecture

```text
User Uploads Multiple PDFs
            │
            ▼
     PDF Text Extraction
            │
            ▼
 Structured Information Extraction
            │
            ▼
      Document Comparison Engine
            │
            ▼
      Key Difference Analysis
            │
            ▼
      AI Insight Generation
            │
            ▼
     Decision Support Summary
            │
            ▼
        Streamlit Interface
```

## Key Design Decisions

* Focus on business and decision-oriented documents.
* Avoid external datasets and web scraping.
* Use user-provided documents as the primary data source.
* Showcase Generative AI capabilities beyond traditional RAG systems.
* Emphasize document understanding, comparison, reasoning, and decision intelligence.
* Maintain a manageable project scope to enable completion within the planned timeline.

---

## Deliverables Completed

* Project title finalized.
* Problem statement documented.
* Solution approach documented.
* Supported document types finalized.
* Comparison output structure finalized.
* Initial architecture defined.
* README.md created and updated.
* Project folder structure initialized.

## Status

Milestone Completed Successfully.

Project is ready for implementation of document upload and text extraction functionality in the next milestone.

# Milestone 2 – Core Application Implementation

## Objective

Implement the complete AI Multi-Document Decision Intelligence Assistant based on the approved requirements, architecture, and supported document categories defined during Milestone 1.

## Features Implemented

### Document Processing

* Multi-PDF Upload
* PDF Text Extraction
* Text Cleaning
* Text Chunking using RecursiveCharacterTextSplitter

### Document Intelligence

* Hybrid Document Title Detection

      * Heuristic Title Detection
      * Gemini Fallback Extraction
      * Filename Fallback

* Hybrid Document Category Detection

      * Keyword-Based Classification
      * Gemini Fallback Classification

### Vector Search & Retrieval

* Embedding Generation using SentenceTransformers (all-MiniLM-L6-v2)
* FAISS Vector Database Creation
* Similarity Search Retrieval
* Top-K Context Retrieval

### Comparison Engine

* Structured Document Summaries
* Executive Comparison Dashboard
* Executive Recommendation
* Quick Decision Guide
* Detailed AI Comparison Report
* Decision Support Summary

### Retrieval-Augmented Generation (RAG)

* Follow-Up Question Support
* Semantic Search
* Context-Based Answer Generation using Gemini 2.5 Flash

### Application Architecture

The application was refactored into a modular architecture consisting of:

* `app.py`
* `config.py`
* `models.py`
* `pdf_processor.py`
* `embeddings.py`
* `vector_store.py`
* `report_generator.py`
* `chat_engine.py`

## Technical Enhancements

### Gemini-Assisted Metadata Extraction

Implemented Gemini-powered title detection and category classification to improve document understanding.

### Structured Summarization Layer

Implemented per-document structured summaries to improve comparison quality and ensure important information from uploaded documents is included in the final report.

### Context Safety Controls

Implemented configurable summarization limits to prevent oversized prompts and maintain predictable latency and cost.

### Error Handling & Fallback Logic

Implemented fallback mechanisms for:

* Title Detection
* Category Classification
* Document Summarization
* PDF Processing

### Executive Dashboard Enhancements

## Deliverables Completed

* Multi-PDF Upload
* PDF Processing Pipeline
* Embedding Generation
* FAISS Indexing
* Document Intelligence Layer
* Comparison Report Generation
* RAG Follow-Up Question Answering
* Modular Architecture Refactor

## Status

**Milestone Completed Successfully**

## Outcome

A fully functional production-ready baseline application has been delivered.

The application is capable of:

* Comparing multiple business documents
* Generating executive comparison dashboards and decision-support reports.
* Supporting follow-up questions using Retrieval-Augmented Generation (RAG)

Future milestones will focus on enhancements and advanced capabilities rather than core functionality development.

# Milestone 3 – Step 1: Agentic AI Foundation

## Objective

Establish the architectural foundation for transforming the existing RAG application into an Agentic AI system without changing existing business functionality.

## Features Implemented

### Agent Framework

* LangGraph integration
* Shared AgentState
* BaseAgent abstraction

### Agents

* Planner Agent
* Retrieval Agent
* Analyzer Agent
* Verifier Agent
* Decision Agent

### Tool Layer

* Search Tool
* Retrieval Tool
* Comparison Tool
* Memory Tool

### Workflow

* LangGraph orchestration
* Sequential agent workflow
* Modular architecture

## Deliverables Completed

* Agent framework
* Tool framework
* LangGraph workflow
* Shared workflow state
* Modular agent architecture

## Status

**Milestone 3 Step 1 Completed Successfully**

## Outcome

The application now has the architectural foundation required for implementing a production-quality Agentic AI workflow while preserving all existing Milestone 2 functionality.

## Next Milestone

### Milestone 3 – Step 2: Multi-Agent Workflow Implementation

Planned enhancements include:

* Planner Agent implementation
* Retrieval Agent implementation
* Analyzer Agent implementation
* Verifier Agent implementation
* Decision Agent implementation
* Agent orchestration using LangGraph
* Integration with the existing RAG pipeline
* Conversation memory
