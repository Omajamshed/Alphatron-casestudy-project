from typing import Dict, Any
from app.db.session import SessionLocal
from app.db.repositories.clause_repo import ClauseRepository
from app.services.ingestion.embedder import get_embedding


def retrieve_standard_terms(state: Dict[str, Any]) -> Dict[str, Any]:
    findings = state.get("findings", [])
    contract_type = state.get("contract_type", "rental")
    standard_terms_map = {}

    db = SessionLocal()
    try:
        clause_repo = ClauseRepository(db)
        for f in findings:
            finding_id = f["id"]
            reason = f["reason"]
            category = f["category"]

            # Query embedding
            emb = get_embedding(f"{category} {reason}")
            scored_docs = clause_repo.search_kb(
                query_embedding=emb,
                contract_type=contract_type,
                top_k=2,
            )
            standard_terms_map[finding_id] = [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "source": doc.source,
                    "category": doc.category,
                }
                for doc, _ in scored_docs
            ]

        return {
            "standard_terms": standard_terms_map,
            "status": "standard_terms_retrieved",
        }
    finally:
        db.close()
