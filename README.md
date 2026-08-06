# AI Multi-Document Decision Intelligence Assistant

## Overview

The AI Multi-Document Decision Intelligence Assistant is a Generative AI and Retrieval-Augmented Generation (RAG) application that helps users compare multiple business documents, identify key differences, generate AI-powered insights, and support decision-making.

Instead of manually reviewing lengthy documents, users can upload multiple PDF files and receive a structured comparison report along with the ability to ask follow-up questions using the uploaded documents as context.

The application is designed for business and personal decision-making scenarios where multiple options must be evaluated before making a final decision.

## Problem Statement

Organizations and individuals frequently compare multiple documents before making important decisions.

Examples include:

* Comparing job offer letters
* Comparing insurance policies
* Comparing loan sanction letters
* Comparing vendor quotations
* Comparing business proposals

Manual comparison is often time-consuming, inconsistent, and prone to overlooking important details.

The objective of this project is to automate document understanding, comparison, and decision support using Generative AI.

## Proposed Solution

The application provides an end-to-end document intelligence workflow:

1. Upload multiple PDF documents
2. Extract document text
3. Detect document titles
4. Detect document categories
5. Generate document chunks
6. Create vector embeddings
7. Store embeddings in FAISS
8. Generate an Executive Comparison Dashboard featuring:
    * Executive Recommendation
    * Quick Decision Guide
    * Detailed AI Comparison Report
    * Decision-oriented insights
9. Support follow-up questions using RAG

The application assists users in making informed decisions but does not make decisions on their behalf.

## Supported Document Types

The system currently supports:

* Offer Letters
* Insurance Policies
* Loan Sanction Letters
* Vendor Quotations
* Business Proposals

The application is optimized for comparing documents belonging to the same category.

## Key Features

### Multi-PDF Upload

Upload and process multiple PDF documents simultaneously.

### Hybrid Document Title Detection

Automatically detects document titles using:

* Heuristic title extraction
* Gemini-based title extraction (only if heuristic confidence is low)
* Filename fallback

### Hybrid Document Category Detection

Automatically classifies uploaded documents using:

* Rule-based keyword matching
* Gemini fallback classification

### Structured Document Summarization

Each document is summarized into a structured business-oriented format before comparison.

### Executive Comparison Dashboard

The application generates:

1. Document Overview
2. Comparison Table
3. Key Differences
4. Executive Recommendation
5. Quick Decision Guide
6. Detailed AI Comparison Report

### Retrieval-Augmented Generation (RAG)

Users can ask follow-up questions after the report is generated.

Responses are generated using:

* Semantic Search
* FAISS Vector Retrieval
* Gemini 2.5 Flash

### Decision Intelligence

The system focuses on helping users compare trade-offs, identify the best option for different priorities, generate executive recommendations, and support informed decision-making.

### Cost Optimizations

The application minimizes LLM usage by:

* Hybrid title detection (heuristics first, Gemini fallback)
* Hybrid category detection (rules first, Gemini fallback)
* Decision-focused document summaries
* Reduced prompt sizes
* Executive report generation from summaries
* Friendly error handling for Gemini quota and availability

## Technology Stack

### Programming Language

* Python

### Frontend

* Streamlit

### PDF Processing

* PyPDF

### Text Processing

* LangChain RecursiveCharacterTextSplitter

### Embedding Model

* SentenceTransformers (all-MiniLM-L6-v2)

### Vector Database

* FAISS

### Large Language Model

* Gemini 2.5 Flash

### Numerical Processing

* NumPy

## Architecture

Multiple PDF Documents
↓
PDF Text Extraction
↓
Title Detection
↓
Category Detection
↓
Text Chunking
↓
SentenceTransformer Embeddings
↓
FAISS Vector Database
↓
LangGraph Agent Orchestrator (Foundation)

Comparison Flow:

Documents
↓
Structured Document Summaries
↓
Comparison Report Generation
↓
Decision Support Insights

RAG Flow:

User Question
↓
Query Embedding
↓
FAISS Similarity Search
↓
Top-K Relevant Chunks
↓
Gemini 2.5 Flash
↓
Answer Generation

## Project Status

Current Status: Milestone 3 - Step 1 Complete

Completed:

* Multi-PDF Upload
* PDF Processing
* Title Detection
* Category Detection
* Embedding Generation
* FAISS Search
* Executive Comparison Dashboard
* Decision Support Recommendations
* Decision-Oriented RAG Follow-Up
* Modular Architecture Refactor
* LangGraph Agent Framework
* Multi-Agent Architecture Foundation
* Shared AgentState
* Agent Orchestrator
* Tool Layer Foundation
* Memory Service Foundation
* Prompt Template Foundation

Next Milestone:

* Multi-Agent Logic Implementation
* Agent Integration with Existing RAG Pipeline
* Conversation Memory
* Verification Workflow
