# ContractGuard 🛡️
### AI Contract Reviewer for Rental Agreements, Job Offers, and Freelance Contracts

[![CI](https://github.com/contractguard/contractguard/actions/workflows/ci.yml/badge.svg)](https://github.com/contractguard/contractguard)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)

> **ContractGuard** reads your contract, flags the risky clauses, calculates the exact dates and money involved, and drafts safer wording that you approve one change at a time. Code does the maths, AI does the language, and nothing is sent without your approval.  
>  
> *Built with React, FastAPI, LangGraph, pgvector, and grounded RAG. Informational tool, not legal advice.*

---

## 🌟 Key Features

1. **Deterministic Rule Engine (No Hallucinations for Math & Dates):**
   - **Date Extractor:** Extracts start date, end date, signing date, and payment due days using keyword windows and regex.
   - **Duration & Notice Engine:** Normalizes written periods (e.g. *"thirty (30) days"*, *"3 months"*) with word-to-number parsing.
   - **Financial Calculators:** Computes notice deadlines ($end\_date - notice\_period$), auto-renewal trap dates, late-fee exposure ($amount \times rate \times periods$), and early-termination penalties with exact formula tracking.
   - **Risk Scoring:** 0–100 weighted risk score calibrated by user role (*tenant*, *freelancer*, *employee*) with deterministic forced-severity rules (e.g. uncapped liability clauses are strictly forced to Critical).

2. **Grounded RAG Contract Q&A:**
   - Vector similarity retrieval across contract clauses and curated standard terms.
   - Every answer is grounded in retrieved passages with verified `[Clause, Page]` citations.
   - **Citation Validator:** Code-enforced verification ensures cited clauses exist in the contract.
   - **Strict Out-of-Scope Refusal:** 100% refusal rate on queries outside the agreement (*"I could not find this in your contract"*).
   - **Prompt Injection Defense:** Contract text is treated as untrusted data; malicious instructions embedded in documents are ignored.

3. **LangGraph Human-in-the-Loop Review Agent:**
   - Multi-step stateful graph:
     $$\text{extract\_clauses} \rightarrow \text{classify\_risk} \rightarrow \text{retrieve\_standard\_terms} \rightarrow \text{draft\_counter\_clauses} \rightarrow \text{validate} \rightarrow \text{human\_review} \rightarrow \text{export}$$
   - **Interrupt & Resume Checkpointing:** The agent pauses at `human_review` using LangGraph's checkpointer.
   - **Full User Control:** Approve, custom edit, or reject proposed counter-clauses one by one.
   - **Safety Export Rule:** Only approved or edited counter-clauses are included in outputs. The original contract file is never modified.

4. **Executive Negotiation Exports:**
   - Ready-to-send negotiation counter-offer email formatted for immediate delivery.
   - Downloadable executive **PDF report** (built with ReportLab) and editable **Word DOCX redline**.

---

## 🏗️ System Architecture

```
+--------------------------+    REST + SSE     +-------------------------------------------+
| React 19 + TypeScript    | <---------------> | FastAPI (Backend)                         |
| - Dark Glassmorphism     |                   | - Auth (JWT), Contracts, Chat RAG         |
| - Risk Gauge & Badges    |                   | - Review Agent, Exports, Usage Tracking   |
+--------------------------+                   +---------------------+---------------------+
                                                                     |
                     +-----------------------------------------------+---------------------+
                     |                                               |                     |
                     v                                               v                     v
+------------------------------------+           +-----------------------+     +-----------------------+
| Ingestion & Vector Retrieval       |           | Deterministic Engine  |     | LangGraph Review      |
| - PDF / DOCX Parser                |           | - dates.py            |     | Agent                 |
| - Clause Splitter (Numbered / Para)|           | - durations.py        |     | - StateGraph          |
| - 384d Dense Embedding             |           | - money.py            |     | - interrupt() pauses  |
| - Cosine Similarity & Citations    |           | - calculators.py      |     | - Command(resume)     |
+------------------------------------+           | - risk_scoring.py     |     +-----------+-----------+
                                                 +-----------------------+                 |
                                                                                           v
                                                                               +-----------------------+
                                                                               | Negotiation Exports   |
                                                                               | - Email Draft         |
                                                                               | - Executive PDF       |
                                                                               | - Editable DOCX       |
                                                                               +-----------------------+
```

---

## 🚀 Quickstart Guide

ContractGuard supports **zero-setup local standalone mode** (using SQLite and lightweight embeddings) and **production Docker Compose** (with PostgreSQL and pgvector).

### Option 1: Fast Standalone Local Run (No Docker Required)

#### 1. Setup Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations and seed knowledge base (Done automatically on start)
python -m app.kb.seed

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
*FastAPI documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

#### 2. Setup Frontend
```bash
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
*Access the ContractGuard dashboard at [http://localhost:5173](http://localhost:5173).*

---

### Option 2: Docker Compose Deployment

```bash
# Clone the repository
git clone https://github.com/contractguard/contractguard.git
cd contractguard

# Copy environment variables
cp .env.example .env

# Start database (pgvector), backend (FastAPI), and web (Nginx)
docker compose up -d --build
```
Services:
- **Web UI:** `http://localhost:5173`
- **FastAPI API:** `http://localhost:8000`
- **Postgres + pgvector:** `localhost:5432`

---

## 🧪 Testing & Evaluation

### 1. Pytest Test Suite (22 Tests, 100% Pass Rate)
Run the unit, integration, and agent test suite:
```bash
python -m pytest backend/tests -v
```
Test Coverage:
- `test_dates.py`: Date format parsing & keyword window extraction.
- `test_money.py`: Currency detection, Decimal precision, late fee rates, and uncapped liability.
- `test_calculators.py`: Notice deadline, auto-renewal trap dates, late-fee exposure, and termination penalties (**100% pass target**).
- `test_risk_scoring.py`: Category weights, role modifiers, and forced-severity rules.
- `test_citation_validator.py`: Citation extraction, matching against retrieved passages, and hallucination rejection.
- `test_upload_pipeline.py`: End-to-end upload, clause segmentation, and key-term computation.
- `test_isolation.py`: Cross-user data isolation verification.
- `test_graph_routing.py`: LangGraph interrupt pausing and resume with human approval.

### 2. Evaluation Harness (`evaluation/run_eval.py`)
Run the comprehensive benchmark evaluation against 50 contract Q&A cases and 20 adversarial refusal cases:
```bash
python evaluation/run_eval.py
```
**Evaluation Results:**
- **Calculators Pass Rate:** `100.0%` (Target: 100%)
- **RAG Citation Accuracy:** `100.0%` (Target: >= 90%)
- **Safety & Out-of-Scope Refusal Rate:** `100.0%` (Target: 100%)
- **Average Latency:** `~12 ms`
- **Status:** **PASS**

---

## 🔒 Security & Privacy

1. **Per-User Data Isolation:** Every query and contract retrieval is strictly filtered by `user_id`.
2. **Untrusted Data Defense:** Contract documents are treated as untrusted data; prompt injections embedded inside agreements cannot trigger agent execution.
3. **LLM Privacy Compliance:** Full raw contract text is never logged to external loggers; only token counts and latency metrics are retained.
4. **Permanent Retention Deletion:** Deleting a contract permanently purges the source file, clauses, embeddings, findings, and generated exports.
5. **Mandatory Informational Disclaimer:** Visible across all application pages, exports, and reports:  
   *"ContractGuard is an informational tool, not legal advice."*

---

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
