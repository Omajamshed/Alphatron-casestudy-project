import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.repositories.clause_repo import ClauseRepository
from app.db.repositories.contract_repo import ContractRepository
from app.services.ingestion.embedder import get_embedding
from app.services.llm.llm_client import llm_client
from app.services.rag.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from app.services.rag.citation_validator import (
    extract_citations_from_text,
    validate_citations_against_retrieved,
)

REFUSAL_RESPONSE = "I could not find this in your contract."


class ContractRAGService:
    def __init__(self, db: Session):
        self.db = db
        self.clause_repo = ClauseRepository(db)
        self.contract_repo = ContractRepository(db)

    def answer_question(
        self,
        version_id: str,
        question: str,
        top_k: int = 4,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        version = self.contract_repo.get_version(version_id)
        if not version:
            return {
                "answer": "Contract version not found.",
                "citations": [],
                "tokens": {"in": 0, "out": 0},
                "seconds": round(time.time() - start_time, 2),
            }

        contract = version.contract
        contract_type = contract.contract_type if contract else "other"
        jurisdiction = contract.jurisdiction if contract else None

        # 1. Embed question
        q_embedding = get_embedding(question)

        # 2. Retrieve top-k clauses from this contract version
        scored_clauses = self.clause_repo.search_clauses(
            version_id=version_id,
            query_embedding=q_embedding,
            top_k=top_k,
        )

        # Enforce code rule: if best similarity score is below threshold, refuse without LLM call
        best_score = scored_clauses[0][1] if scored_clauses else 0.0
        if not scored_clauses or best_score < settings.SIMILARITY_THRESHOLD:
            return {
                "answer": REFUSAL_RESPONSE,
                "citations": [],
                "tokens": {"in": 0, "out": 0},
                "seconds": round(time.time() - start_time, 2),
            }

        retrieved_clauses = [c for c, _ in scored_clauses]

        # 3. Retrieve KB entries
        scored_kb = self.clause_repo.search_kb(
            query_embedding=q_embedding,
            contract_type=contract_type,
            jurisdiction=jurisdiction,
            top_k=2,
        )
        retrieved_kb = [doc for doc, _ in scored_kb]

        # 4. Construct prompt passages
        contract_passages = "\n\n".join([
            f"--- [Clause {c.clause_no or 'General'}, Page {c.page_start}] {c.heading or ''} ---\n{c.text}"
            for c in retrieved_clauses
        ])
        kb_passages = "\n\n".join([
            f"--- Market Standard: {doc.title} ({doc.source or 'General'}) ---\n{doc.content}"
            for doc in retrieved_kb
        ])

        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            contract_passages=contract_passages,
            kb_passages=kb_passages,
            question=question,
        )

        # 5. Call LLM
        res = llm_client.invoke(
            user_prompt=user_prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
            feature="chat_rag",
            user_id=user_id,
            db=self.db,
            contract_id=contract.id if contract else "",
        )

        answer_text = res["content"].strip()

        # 6. Validate citations
        raw_citations = extract_citations_from_text(answer_text)
        is_valid, validated_citations = validate_citations_against_retrieved(
            raw_citations,
            retrieved_clauses,
        )

        # If invalid citations, retry once with explicit warning
        if not is_valid and raw_citations:
            retry_prompt = (
                user_prompt +
                "\n\nCRITICAL: In your previous attempt you cited clauses that were NOT in the retrieved passages. "
                "You must cite ONLY the exact clause numbers provided above (e.g. " +
                ", ".join([c.clause_no for c in retrieved_clauses if c.clause_no]) +
                ")."
            )
            res = llm_client.invoke(
                user_prompt=retry_prompt,
                system_prompt=RAG_SYSTEM_PROMPT,
                feature="chat_rag_retry",
                user_id=user_id,
                db=self.db,
                contract_id=contract.id if contract else "",
            )
            answer_text = res["content"].strip()
            raw_citations = extract_citations_from_text(answer_text)
            _, validated_citations = validate_citations_against_retrieved(
                raw_citations,
                retrieved_clauses,
            )

        # If model answered affirmatively without citation, attach primary retrieved clause as citation
        if not validated_citations and retrieved_clauses and REFUSAL_RESPONSE.lower() not in answer_text.lower():
            validated_citations.append({
                "file": version.filename or "contract.pdf",
                "clause": retrieved_clauses[0].clause_no or "1.0",
                "page": retrieved_clauses[0].page_start,
                "clause_id": retrieved_clauses[0].id,
                "heading": retrieved_clauses[0].heading,
            })

        return {
            "answer": answer_text,
            "citations": validated_citations,
            "tokens": {"in": res["tokens_in"], "out": res["tokens_out"]},
            "seconds": round(time.time() - start_time, 2),
        }
