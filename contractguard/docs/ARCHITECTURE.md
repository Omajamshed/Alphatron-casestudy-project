# ContractGuard: System Architecture & Design Specification

> **AI contract reviewer for rental agreements, job offers, and freelance contracts.**  
> *Stack: React, Vite, TypeScript, FastAPI, RAG, LangGraph, PostgreSQL with pgvector, Deterministic Rule Engine.*

---

## 1. Design Principle
**"Code does the maths, the AI does the language."**
- Date extraction, notice-period deadlines, penalty exposure, and risk scoring run in deterministic Python so results are exact and 100% testable.
- The LLM is used strictly to classify clause nuances, explain risk in plain language, and draft balanced counter-clauses grounded in curated standard terms.

---

## 2. End-to-End Workflow Diagram

```
+--------------------+            +--------------------------------------------+
| React 19 Frontend  |  REST/SSE  |                FastAPI                     |
| (Vite + TypeScript)| <--------> |  routes: auth, contracts, chat, risk,     |
+--------------------+            |          review, exports, usage            |
                                  +---------------------+----------------------+
                                                        |
         +----------------------------------------------+--------------------+
         |                                              |                    |
         v                                              v                    v
+-----------------------+                    +--------------------+   +--------------+
| Ingestion & Splitting |                    | Deterministic Rule |   | LangGraph    |
| - PDF/DOCX Parser     |                    | Engine             |   | Review Agent |
| - Clause Splitter     |                    | - dates.py         |   | - StateGraph |
| - 384d Embedder       |                    | - durations.py     |   | - interrupt  |
| - Cosine Retrieval    |                    | - money.py         |   | - checkpoint |
+-----------------------+                    | - renewal.py       |   +-------+------+
                                             | - calculators.py   |           |
                                             | - risk_scoring.py  |           |
                                             +--------------------+           |
                                                                              v
                                                                   +--------------------+
                                                                   | Human Approval &   |
                                                                   | Export Generation  |
                                                                   | - Negotiation Email|
                                                                   | - PDF & DOCX Docs  |
                                                                   +--------------------+
```

---

## 3. LangGraph Review Workflow

```
START -> extract_clauses -> classify_risk --(no findings)--> END (low risk summary)
              |
              v
       retrieve_standard_terms
              |
              v
       draft_counter_clauses <----+
              |                   | retry once
              v                   |
           validate --------------+
              |
              v
       human_review (interrupt, waits for user decisions)
              |
              v
           export (builds email + PDF/DOCX from approved items only)
              |
              v
             END
```

---

## 4. Deterministic Calculations
All money calculations use Python's `decimal.Decimal` to avoid floating point drift.
1. **Notice Deadline:**
   $$\text{Notice Deadline} = \text{End Date} - \text{Notice Period (Days)}$$
2. **Auto-Renewal Trap Date:**
   $$\text{Trap Date} = \text{End Date} - \text{Cancellation Window (Days)}$$
3. **Late-Fee Exposure:**
   $$\text{Exposure} = \text{Amount} \times \text{Rate} \times \text{Periods Late}$$
4. **Early-Termination Penalty:**
   $$\text{Penalty} = \text{Remaining Months} \times \text{Monthly Rent (or fixed fee)}$$
5. **Weighted Contract Risk Score:**
   $$\text{Score} = \min\left(100, \frac{\sum (\text{Severity Score} \times \text{Category Weight})}{\text{Max Possible}} \times 100\right)$$
   *(Uncapped liability clauses deterministically force critical status $\ge 65$)*

---

## 5. Security, Privacy & Safety
- **Per-User Isolation:** Every contract query is scoped by authenticated `user_id`.
- **Untrusted Contract Data:** Contract text is marked as untrusted data; prompt injections embedded inside contract documents are ignored.
- **Citation Verification:** Responses must reference retrieved clause IDs. Answers with hallucinations are retried and scrubbed.
- **Privacy Compliance:** Raw contract text is never logged to external log aggregators; only token counts and latency metrics are tracked.
- **Informational Disclaimer:** Every report, API response, and screen carries the notice: *"ContractGuard is an informational tool, not legal advice."*
