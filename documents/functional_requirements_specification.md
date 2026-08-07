# AI Multi-Document Decision Intelligence Assistant

## Functional Requirements Specification (FRS)

### Version

3.3

### Status

Approved and Implemented (Milestone 3 - Step 3)

## Project Objective

The objective of the application is to help users compare multiple business documents and generate structured decision-support insights using Generative AI and Retrieval-Augmented Generation (RAG).

Users can upload multiple PDF documents and receive AI-generated comparison reports that highlight similarities, differences, risks, benefits, and recommendations.

## Supported Document Types

The application shall support:

### Career Decisions

* Offer Letters

### Financial Decisions

* Insurance Policies
* Loan Sanction Letters

### Procurement Decisions

* Vendor Quotations

### Business Strategy Decisions

* Business Proposals

The system shall support comparison of two or more documents belonging to the same category.

## User Workflow

### Step 1

User uploads multiple PDF documents.

### Step 2

System extracts text from uploaded PDFs.

### Step 3

System automatically detects document titles.

### Step 4

System automatically detects document categories.

### Step 5

System creates document chunks.

### Step 6

System generates embeddings.

### Step 7

System stores embeddings in FAISS.

### Step 8

System generates structured document summaries.

### Step 9

System generates a comparison report.

### Step 10

User may ask follow-up questions using natural language.

### Step 11

System retrieves relevant document chunks and produces concise executive decision answers grounded in retrieved evidence.

## Mandatory Output Sections

Every comparison report shall contain:

### 1. Document Overview

Provides:

* Document Title
* Document Category
* Purpose
* Key Highlights

### 2. Comparison Table

Provides side-by-side comparison of:

* Financial Terms
* Benefits
* Obligations
* Risks
* Exclusions
* Important Conditions
* Validity Information

### 3. Key Differences

Highlights major differences between documents.

### 4. AI Insights

Provides:

* Risk Analysis
* Benefit Analysis
* Cost Considerations
* Strategic Observations

### 5. Decision Support Summary

Provides:

* Recommended Choice

* Top 3 Decision Reasons

* Executive Recommendation

### Follow-Up Question Capability

The system shall answer questions using retrieved document context and provide concise executive decision support instead of document retrieval summaries.

Example Questions:

* Which insurance policy has fewer exclusions?
* Which offer letter provides better benefits?
* Which quotation provides the best value?
* Which proposal has lower implementation risk?

The system shall answer questions using retrieved document context.

## Document Intelligence Requirements

### Title Detection

The system shall automatically detect document titles using:

1. Heuristic extraction
2. Gemini fallback extraction
3. Filename fallback

### Category Detection

The system shall automatically classify documents using:

1. Keyword-based classification
2. Gemini fallback classification

Supported categories:

* Offer Letters
* Insurance Policies
* Loan Sanction Letters
* Vendor Quotations
* Business Proposals

### Document Summarization

The system shall generate structured summaries for each uploaded document prior to comparison.

Summary fields include:

* Purpose
* Financial Terms
* Benefits
* Obligations
* Risks
* Exclusions
* Validity Period
* Important Conditions

## Non-Functional Requirements

### Performance

The system should process typical business documents within acceptable response times.

### Reliability

The application shall gracefully handle:

* Missing fields
* Empty documents
* Classification failures
* Summarization failures

### Explainability

Responses should be generated from uploaded documents and retrieved context.

### Scalability

Document summarization shall use configurable context limits to avoid oversized prompts.

## Technical Architecture

### Frontend

* Streamlit

### PDF Processing

* PyPDF

### Text Chunking

* LangChain RecursiveCharacterTextSplitter

### Embedding Model

* SentenceTransformers (all-MiniLM-L6-v2)

### Vector Database

* FAISS

### Large Language Model

* Gemini 2.5 Flash

### Retrieval Method

* Similarity Search

### Comparison Engine

* Structured Document Summaries
* Executive Comparison Dashboard
* Executive Recommendation
* Quick Decision Guide
* Detailed AI Comparison Report

### RAG Engine

* Query Embeddings
* Vector Retrieval
* Context-Based Answer Generation

### Agent Orchestration

* LangGraph Workflow
* Shared AgentState
* Planner Agent
* Retrieval Agent
* Analyzer Agent
* Verifier Agent
* Decision Agent
* Search Tool
* Conversation Memory

## Milestone 3 Step 2 Deliverables

Completed:

* Multi-PDF Upload
* PDF Extraction
* Text Chunking
* Embedding Generation
* FAISS Indexing
* Hybrid Title Detection
* Hybrid Category Detection
* Structured Document Summaries
* Comparison Report Generation
* Follow-Up Question Support
* Modular Architecture
* LangGraph Integration
* Multi-Agent Framework
* Shared AgentState
* Tool Layer
* Agent Orchestrator
* Evidence Coverage Verification
* Confidence-Based Validation
* AI Guardrails

Milestone 3 Step 3 strengthens the multi-agent workflow by validating evidence coverage, computing confidence based on retrieved information, and introducing AI guardrails to reduce unsupported conclusions while preserving the existing RAG comparison pipeline.

## Future Enhancements

Future milestones may include:

* Conversation Memory
* Workflow Visualization
* Deployment
* Production Monitoring
* Enhanced Source Attribution
* Report Export
* Additional Document Categories
* Visualization Enhancements
