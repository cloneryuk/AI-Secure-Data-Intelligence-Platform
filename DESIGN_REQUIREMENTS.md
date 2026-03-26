# AI Secure Data Intelligence Platform - Design & Architecture Requirements

This document outlines the core requirements, architecture design, and technical approach to building the AI Secure Data Intelligence Platform as per the SISA Hackathon specifications.

## 1. Goal Description
To develop a multi-functional system that serves as an AI Gateway, Data Scanner, Log Analyzer, and Risk Engine. It must securely ingest multiple data formats (logs, text, files, SQL, chat), parse them to identify secrets (PII, credentials, API keys) via regex and AI, assigning risk scores, and present these insights on an interactive frontend dashboard.

## 2. Core Modules & Engine

### 2.1 Input & Validation Layer
*   **API Gateway (`/analyze` endpoint):** The primary entry point capable of receiving diverse payloads. Needs robust validation to handle `text`, `file` (base64 or multipart), `sql`, `chat`, and particularly `log` files. Includes a Rate Limiter to gracefully reject or queue excessively large payloads (e.g., >500MB).
*   **File Parsers:** Extract plain text from `.pdf`, `.docx`, and `.txt` files.

### 2.2 Detection Engine
*   **Regex / Pattern Matching Component:** Deterministically fast-scan for known high/critical risks:
    *   Emails (Low Risk)
    *   Phone Numbers
    *   API Keys (High Risk)
    *   Passwords (Critical Risk)
*   **Log Analyzer Module (New capability):**
    *   Generator-based parsing to process large logs line by line (or chunk-by-chunk) to avoid memory overload.
    *   Responsible for detecting stack traces, suspicious IP activity, and repeated failures.
*   **AI Analyzer:** Leveraging an LLM (OpenAI, Anthropic, or local) to deduce contextual insights from logs. E.g., interpreting unstructured application logs to conclude "Multiple failed login attempts detected" or "Sensitive credentials exposed in logs."
    *   **CRITICAL REDACTION STEP:** Before sending raw logs to the external API, all Regex-identified secrets must be replaced with `[REDACTED_SECRET]` to prevent data breaches while preserving context for the AI.

### 2.3 Risk & Policy Engine
*   **Risk Engine:** Aggregates findings from the Regex and AI outputs, mapping them to exact risk levels (Low, Medium, High, Critical) and computing a final quantitative risk score.
*   **Policy Engine:** Based on the risk level and input `options` (e.g., `block_high_risk: true`), dictates the final response action such as `masked`, `blocked`, or `allowed`. The policy engine never permanently overwrites the original log file; the masked log is returned as a new string or file in the JSON response to preserve original evidence.

### 2.4 Frontend Dashboard (UI)
*   **Log Upload Interface:** Drag-and-drop support tailored for `.log` and `.txt` formats.
*   **Log Visualization:** A rich text viewer that displays log lines, highlighting those containing sensitive data, side-by-side with line numbers.
*   **Insights Panel:** A dashboard summarizing AI-generated reports, security warnings, risk level breakdown, and raw findings.

### 2.5 Observability
*   **Logging & Monitoring:** Basic infrastructure tracking API request times, error rates, and payload sizes using Python's native logging or FastAPI middleware to ensure the platform is production-ready.

## 3. Recommended Technology Stack

We suggest a modern, scalable approach to fulfill the hackathon's evaluation criteria:

*   **Backend & Data Processing:** Python with **FastAPI**. Python excels at text processing, regex operations, log chunking, and AI integrations.
*   **Frontend UI:** **React.js** (or Next.js) with Tailwind CSS for rapid prototyping of a visually appealing log upload and preview dashboard.
*   **AI Integration:** **OpenAI API** (gpt-4o-mini or gpt-3.5-turbo) or **Anthropic Claude** for fast, high-quality semantic analysis of log chunks. Optionally, Hugging Face models for strict data privacy.
*   **Deployment:** Dockerize the frontend and backend, deployed to Render, Vercel (for frontend), or an AWS EC2 instance.

## 4. End-to-End Processing Workflow
1. Client submits log file via the React UI.
2. FastAPI backend receives file, validates it (including rate limiting check), and streams it chunk-by-chunk.
3. The Regex Engine detects hardcoded secrets on specific lines.
4. Redaction Step: Detected secrets are explicitly masked (`[REDACTED_SECRET]`) before external API submission.
5. The AI Engine analyzes the cleansed chunk to discover anomalies and generate holistic insights.
6. Risk Engine scores the findings and Policy Engine formulates an action.
7. Unified JSON response is returned (including the new masked log string, leaving the original intact).
8. React UI renders highlighted logs, risk breakdowns, and AI insights.

## 5. Deployment & Evaluation Focus
To maximize the evaluation criteria marks:
*   Ensure **Backend Design (18)** is modularized into distinct services (Gateway, Parser, Risk Engine).
*   Ensure **AI Integration (15)** goes beyond simple pattern matching into actual log summarization.
*   Ensure **Log Analysis (15)** can handle parsing line numbers effectively to map findings accurately.
